import uuid
import logging
from typing import AsyncGenerator, List, Optional
from fastapi import Depends
from ai.common import BaseChatMessage, BaseToolCallWithResult, ChatRole
from .user_service import UserService
from .instructor_service import InstructorService
from app.repositories import ChatRepository, CourseRepository
from domain.schema.chat.chat_message import ChatMessage
from domain.schema.chat.chat_session import ChatSession
from domain.dto.chat.chat_message import ChatMessageDto
from domain.dto.ai import CompletionChunk
from domain.enums.chat_enums import PromptType
from ai.prompts import LessonDiscussionPrompt

logger = logging.getLogger("ChatService")

class ChatService:
    user_service: UserService
    instructor_service: InstructorService
    chat_repository: ChatRepository
    course_repository: CourseRepository
    
    def __init__(
        self, 
        user_service: UserService = Depends(UserService),
        instructor_service: InstructorService = Depends(InstructorService),
        chat_repository: ChatRepository = Depends(ChatRepository),
        course_repository: CourseRepository = Depends(CourseRepository)
    ):
        self.user_service = user_service
        self.instructor_service = instructor_service
        self.chat_repository = chat_repository
        self.course_repository = course_repository

    async def create_session(
        self,
        user_id: str,
        prompt_type: PromptType,
        resource_id: Optional[uuid.UUID] = None
    ) -> uuid.UUID:
        """
        Creates a new chat session for a user.

        Args:
            user_id (str): The ID of the user creating the session.
            prompt_type (PromptType): The type of prompt for this chat session.
            resource_id (Optional[uuid.UUID], optional): The ID of the associated resource, if any. Defaults to None.

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
        
        # Get the instructor associated with the user
        instructor = await self.instructor_service.get_user_instructor(user.id)
        
        # Ensure the instructor exists
        if not instructor:
            raise ValueError("Instructor not found")
        
        # Create a new chat session in the repository
        session = await self.chat_repository.create_chat_session(
            user_id=user.id,
            prompt_type=prompt_type.value,
            resource_id=resource_id,
            instructor_id=instructor.id
        )
        
        # Return the ID of the newly created session
        return session.id

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
        message: str
    ) -> AsyncGenerator[CompletionChunk, None]:
        user = await self.user_service.get_user("id", user_id, ["profile.*"])
        
        if not user:
            raise ValueError("User not found")
        
        session = await self.chat_repository.get_session(session_id)
        
        logger.info(f"Preparing to generate chat response for user {user.id}, session {session.id}")

        response_generator = self.get_prompt_generator(
            session=session,
            input_msg=message
        )
        
        try:
            async for chunk in response_generator:
                yield chunk
        except StopAsyncIteration:
            # The generator has been exhausted, which is expected behavior
            pass
        
        messages: List[BaseChatMessage] = response_generator.aclose()
        
        await self._add_message(
            session_id=session_id, 
            is_user=True, 
            message=message
        )
        
        for new_message in messages:
            await self._add_message(
                session_id=session_id, 
                is_user=new_message.role == ChatRole.USER, 
                message=new_message.message, 
                tool_calls=new_message.tool_calls
            )
    
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
                        id=tool_call.id,
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
        is_user: bool, 
        message: str,
        tool_calls: List[BaseToolCallWithResult] = []
    ) -> None:
        added_msg = await self.chat_repository.add_chat_message(
            session_id=session_id, 
            is_user=is_user, 
            content=message
        )
        
        if tool_calls:
            for tool_call in tool_calls:
                self.chat_repository.add_tool_message(
                    message_id=added_msg.id,
                    call_id=tool_call.id,
                    tool_name=tool_call.name,
                    arguments=tool_call.arguments,
                    result=tool_call.result
                )
                
    async def get_prompt_generator(
        self,
        session: ChatSession,
        input_msg: str
    ) -> AsyncGenerator[CompletionChunk, None]:
        p_type = PromptType(session.prompt_type)
        
        messages = await self.chat_repository.get_chat_messages(session.id)
        model_messages = self._get_chat_messages(messages)
        
        if p_type == PromptType.LESSON:
            if session.resource_id is None:
                raise ValueError("Resource ID is required for lesson prompt")
            
            lesson = await self.course_repository.get_lesson(session.resource_id)
            
            prompt = LessonDiscussionPrompt()
            async for chunk, _, is_final in await prompt.get_responses(
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
            raise ValueError("Invalid prompt type")