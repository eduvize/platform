import uuid
import logging
import asyncio
from collections import deque
from typing import AsyncGenerator, AsyncIterator, List, Optional, Tuple
from fastapi import Depends, HTTPException, status
from ai.common import BaseChatMessage, BaseToolCallWithResult, ChatRole
from .user_service import UserService
from .instructor_service import InstructorService
from .voice_service import VoiceService
from app.repositories import ChatRepository, CourseRepository
from domain.schema.chat.chat_message import ChatMessage
from domain.schema.chat.chat_session import ChatSession
from domain.schema.instructors.instructor import Instructor
from domain.dto.chat.chat_message import ChatMessageDto
from domain.dto.ai import CompletionChunk
from domain.enums.chat_enums import PromptType
from ai.prompts import LessonDiscussionPrompt, OnboardingInstructorSelectionPrompt, OnboardingProfileBuilderPrompt

logger = logging.getLogger("ChatService")

class ChatService:
    user_service: UserService
    instructor_service: InstructorService
    chat_repository: ChatRepository
    course_repository: CourseRepository
    voice_service: VoiceService
    
    def __init__(
        self, 
        user_service: UserService = Depends(UserService),
        instructor_service: InstructorService = Depends(InstructorService),
        chat_repository: ChatRepository = Depends(ChatRepository),
        course_repository: CourseRepository = Depends(CourseRepository),
        voice_service: VoiceService = Depends(VoiceService)
    ):
        self.user_service = user_service
        self.instructor_service = instructor_service
        self.chat_repository = chat_repository
        self.course_repository = course_repository
        self.voice_service = voice_service

    async def create_session(
        self,
        user_id: str
    ) -> ChatSession:
        """
        Creates a new chat session for a user.

        Args:
            user_id (str): The ID of the user creating the session.
            instructor_id (Optional[uuid.UUID], optional): The ID of the instructor for this chat session. Defaults to None.

        Returns:
            uuid.UUID: The ID of the newly created chat session.

        Raises:
            ValueError: If the user or instructor is not found.
        """
        # Fetch the user from the database
        user = await self.user_service.get_user("id", user_id)
        
        # Ensure the user exists
        if not user:
            raise ValueError("User not found")
        
        # Create a new chat session in the repository
        session = await self.chat_repository.create_chat_session(
            user_id=user.id,
        )
        
        return session

    async def get_history(
        self,
        user_id: str,
        session_id: uuid.UUID
    ) -> List[ChatMessageDto]:
        user = await self.user_service.get_user("id", user_id)
        
        if not user:
            raise ValueError("User not found")
        
        messages = await self.chat_repository.get_chat_messages(session_id)
        
        return [
            ChatMessageDto.model_validate(message)
            for message in messages
        ]
    
    async def get_response(
        self, 
        user_id: str,
        session_id: uuid.UUID,
        instructor_id: uuid.UUID,
        prompt_type: PromptType,
        message: Optional[str] = None,
        audio: Optional[str] = None,
        expect_audio_response: bool = False
    ) -> AsyncGenerator[CompletionChunk, None]:
        user = await self.user_service.get_user("id", user_id, ["profile.*"])
        
        if not user:
            raise ValueError("User not found")
        
        session = await self.chat_repository.get_session(session_id)
        instructor = await self.instructor_service.get_instructor_by_id(instructor_id)
        
        logger.info(f"Preparing to generate chat response for user {user.id}, session {session.id}")

        if audio:
            message = await self.voice_service.speech_to_text(audio)
            
            # If the message is empty, close out of this function
            if not message:
                return
            
            yield CompletionChunk.model_construct(received_text=message)

        response_generator, final_messages_future = await self.get_prompt_generator(
            session=session,
            instructor=instructor,
            prompt_type=prompt_type,
            input_msg=message
        )
        
        speech_queue = asyncio.Queue()
        audio_queue = asyncio.Queue()
        
        # Start background task for audio generation
        audio_task = asyncio.create_task(self._generate_audio(speech_queue, audio_queue, instructor.voice_id))
        
        speech_buffer = ""
        word_count = 0
        async for chunk in response_generator:
            if chunk.text or chunk.tools:
                yield CompletionChunk.model_construct(message_id=chunk.message_id, text=chunk.text, tools=chunk.tools)
            
            if chunk.text:
                speech_buffer += chunk.text.encode("ascii", "ignore").decode("ascii") # Take only ASCII characters
                current_words = speech_buffer.split()
                word_count = len(current_words)
            
                if chunk.text.strip().endswith(('.', '?', '!')) and expect_audio_response and word_count > 1:
                    await speech_queue.put(speech_buffer)
                    speech_buffer = ""
                    word_count = 0
        
        # Handle any remaining text in the buffer
        if speech_buffer and expect_audio_response and word_count > 1:
            await speech_queue.put(speech_buffer)
        elif speech_buffer:
            # If there's remaining text but not enough words, add it to the next chunk
            await speech_queue.put(speech_buffer)
        
        # Signal that no more text is coming
        await speech_queue.put(None)
        
        # Yield any remaining audio chunks
        while True and expect_audio_response:
            audio_chunk = await audio_queue.get()
            if audio_chunk is None:
                break
            yield CompletionChunk.model_construct(audio=audio_chunk)
        
        # Ensure we always add messages to the database
        await self._add_message(
            session_id=session.id,
            is_user=True,
            message=message,
            sender_id=user.id
        )
        
        try:
            final_messages = await final_messages_future
            if final_messages:
                for new_message in final_messages:
                    await self._add_message(
                        session_id=session.id,
                        is_user=new_message.role == ChatRole.USER,
                        message=new_message.message,
                        sender_id=instructor.id,
                        tool_calls=new_message.tool_calls
                    )
        except Exception as e:
            logger.error(f"Error processing final messages: {str(e)}")

    async def _generate_audio(self, speech_queue: asyncio.Queue, audio_queue: asyncio.Queue, voice_id: str):
        """Background task to generate audio from text chunks."""
        try:
            while True:
                text_chunk = await speech_queue.get()
                if text_chunk is None:
                    await audio_queue.put(None)
                    break
                
                base64_audio = await self.voice_service.get_base64_chunk(text_chunk, voice_id)
                await audio_queue.put(base64_audio)
        except Exception as e:
            logger.error(f"Error in audio generation: {str(e)}")
            await audio_queue.put(None)

    def _get_chat_messages(
        self,
        records: List[ChatMessage]
    ) -> List[BaseChatMessage]:
        """
        Converts chat message records into a representation for the AI

        Args:
            records (List[ChatMessage]): The chat messages to convert

        Returns:
            List[BaseChatMessage]: The converted messages
        """
        
        return [
            BaseChatMessage(
                role=ChatRole.USER if record.is_user else ChatRole.AGENT,
                message=record.content,
                png_images=[],
                tool_calls=[
                    BaseToolCallWithResult(
                        id=tool_call.tool_call_id,
                        name=tool_call.tool_name,
                        arguments=tool_call.json_arguments,
                        result=tool_call.result
                    )
                    for tool_call in record.tool_calls
                ]
            )
            for record in records
        ]
            
    async def _add_message(
        self, 
        session_id: uuid.UUID,
        sender_id: uuid.UUID,
        is_user: bool, 
        message: str,
        tool_calls: List[BaseToolCallWithResult] = []
    ) -> None:
        added_msg = await self.chat_repository.add_chat_message(
            session_id=session_id, 
            is_user=is_user, 
            content=message,
            sender_id=sender_id
        )
        
        if tool_calls:
            for tool_call in tool_calls:
                await self.chat_repository.add_tool_message(
                    message_id=added_msg.id,
                    call_id=tool_call.id,
                    tool_name=tool_call.name,
                    arguments=tool_call.arguments,
                    result=tool_call.result
                )
                
    async def get_prompt_generator(
        self,
        session: ChatSession,
        instructor: Instructor,
        prompt_type: PromptType,
        input_msg: str
    ) -> Tuple[AsyncGenerator[CompletionChunk, None], asyncio.Future]:
        messages = await self.chat_repository.get_chat_messages(session.id)
        model_messages = self._get_chat_messages(messages)
        
        final_messages_future = asyncio.Future()

        async def response_wrapper():
            final_messages = []
            try:
                if prompt_type == PromptType.LESSON:
                    if session.resource_id is None:
                        raise ValueError("Resource ID is required for lesson prompt")

                    lesson = await self.course_repository.get_lesson(session.resource_id)
                    
                    prompt = LessonDiscussionPrompt()
                    async for chunk, responses, is_final in await prompt.get_responses(
                        instructor=instructor,
                        history=model_messages,
                        new_message=input_msg,
                        lesson_content="\n\n".join(
                            [
                                f"{section.title}\n{section.content}" 
                                for section in lesson.sections
                            ]
                        )
                    ):
                        if not is_final:
                            yield chunk
                        else:
                            final_messages = responses
                            break
                elif prompt_type == PromptType.ONBOARDING:
                    prompt = OnboardingInstructorSelectionPrompt()
                    async for chunk, responses, is_final in await prompt.get_responses(
                        instructor=instructor,
                        history=model_messages,
                        new_message=input_msg
                    ):
                        if not is_final:
                            yield chunk
                        else:
                            final_messages = responses
                            break
                elif prompt_type == PromptType.PROFILE_BUILDER:
                    prompt = OnboardingProfileBuilderPrompt()
                    async for chunk, responses, is_final in await prompt.get_responses(
                        instructor=instructor,
                        history=model_messages,
                        new_message=input_msg
                    ):
                        if not is_final:
                            yield chunk
                        else:
                            final_messages = responses
                            break
            except Exception as e:
                logging.error(f"Error in get_prompt_generator: {e}")
                raise e
            finally:
                final_messages_future.set_result(final_messages)

        return response_wrapper(), final_messages_future
