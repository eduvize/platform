import uuid
import logging
from typing import AsyncGenerator, List, Optional
from fastapi import Depends
from ai.common import BaseChatMessage, BaseToolCallWithResult, ChatRole
from app.services import UserService
from app.utilities.profile import get_user_profile_text
from app.repositories import ChatRepository, CourseRepository
from app.routing.contracts.chat_contracts import SendChatMessage, ChatSessionReference
from domain.schema.chat.chat_message import ChatMessage
from domain.dto.chat.chat_message import ChatMessageDto
from domain.dto.profile import UserProfileDto
from domain.dto.ai import CompletionChunk

logger = logging.getLogger("ChatService")

class ChatService:
    user_service: UserService
    chat_repository: ChatRepository
    course_repository: CourseRepository
    
    def __init__(
        self, 
        user_service: UserService = Depends(UserService),
        chat_repository: ChatRepository = Depends(ChatRepository),
        course_repository: CourseRepository = Depends(CourseRepository)
    ):
        self.user_service = user_service
        self.chat_repository = chat_repository
        self.course_repository = course_repository
        
    async def get_history(
        self,
        user_id: str,
        payload: Optional[ChatSessionReference] = None
    ) -> List[ChatMessageDto]:
        user = await self.user_service.get_user("id", user_id)
        
        if not user:
            raise ValueError("User not found")
        
        session_id = self._get_chat_session_id(user.id, payload)
        
        messages = self.chat_repository.get_chat_messages(session_id)
        
        return [
            ChatMessageDto.model_validate(message)
            for message in messages
        ]
    
    async def get_response(
        self, 
        user_id: str,
        payload: SendChatMessage
    ) -> AsyncGenerator[CompletionChunk, None]:
        user = await self.user_service.get_user("id", user_id, ["profile.*", "instructor"])
        
        if not user:
            raise ValueError("User not found")
        
        logger.info(f"Preparing to generate chat response for user {user.id}")
        
        profile_dto = UserProfileDto.model_validate(user.profile)
        user_profile_text = get_user_profile_text(profile_dto)
        
        session_id = self._get_chat_session_id(user.id, payload)
        
        logger.info(f"Using chat session {session_id}")
        
        messages = self.chat_repository.get_chat_messages(session_id)
        logger.info(f"Retrieved {len(messages)} messages from the chat session")
        
        model_messages = self._get_chat_messages(messages)
        
        logger.info(f"Calling model for response generation")
        #prompt = CoursePlanningPrompt()
        #responses = prompt.get_response(
        #    instructor_name=user.instructor.name,
        #    profile_text=user_profile_text,
        #    history=model_messages, 
        #    message=payload.message
        #)
        
        # Iterate until complete, then save messages to the database
        #while True:
        #    try:
        #        yield next(responses)
        #    except StopIteration as e:
        #        messages: List[BaseChatMessage] = e.value
        #        
        #        self._add_message(
        #            session_id=session_id, 
        #            is_user=True, 
        #            message=payload.message
        #        )
        #        
        #        for new_message in messages:
        #            self._add_message(
        #                session_id=session_id, 
        #                is_user=new_message.role == ChatRole.USER, 
        #                message=new_message.message, 
        #                tool_calls=new_message.tool_calls
        #            )
        #        
        #        break
    
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
            
    def _get_chat_session_id(
        self,
        user_id: uuid.UUID,
        reference: Optional[ChatSessionReference]
    ) -> uuid.UUID:
        if not reference:
            return self.chat_repository.get_default_session(user_id)
        
        if reference.curriculum_id:
            return self.chat_repository.get_session_by_curriculum(user_id, reference.curriculum_id)
        elif reference.lesson_id:
            return self.chat_repository.get_session_by_lesson(user_id, reference.lesson_id)
        elif reference.exercise_id:
            return self.chat_repository.get_session_by_exercise(user_id, reference.exercise_id)
        else:
            return self.chat_repository.get_default_session(user_id)
            
    def _add_message(
        self, 
        session_id: uuid.UUID, 
        is_user: bool, 
        message: str,
        tool_calls: List[BaseToolCallWithResult] = []
    ) -> None:
        added_msg = self.chat_repository.add_chat_message(
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