import uuid
import logging
from typing import AsyncGenerator, Generator, List, Optional
from fastapi import Depends
from ai.common import BaseChatMessage, BaseToolCallWithResult, ChatRole
from app.services import UserService
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

    async def create_session(
        self,
        user_id: str,
        prompt_type: PromptType,
        resource_id: Optional[uuid.UUID] = None
    ) -> uuid.UUID:
        user = await self.user_service.get_user("id", user_id)
        
        if not user:
            raise ValueError("User not found")
        
        session = self.chat_repository.create_chat_session(
            user_id=user.id,
            prompt_type=prompt_type.value,
            resource_id=resource_id
        )
        
        return session.id

    async def get_history(
        self,
        user_id: str,
        session_id: uuid.UUID
    ) -> List[ChatMessageDto]:
        user = await self.user_service.get_user("id", user_id)
        
        if not user:
            raise ValueError("User not found")
        
        messages = self.chat_repository.get_chat_messages(session_id)
        
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
        
        session = self.chat_repository.get_session(session_id)
        
        logger.info(f"Preparing to generate chat response for user {user.id}, session {session.id}")

        response_generator = self.get_prompt_generator(
            session=session,
            input=message
        )
        
        # Iterate until complete, then save messages to the database
        while True:
            try:
                yield next(response_generator)
            except StopIteration as e:
                messages: List[BaseChatMessage] = e.value
                
                self._add_message(
                    session_id=session_id, 
                    is_user=True, 
                    message=message
                )
                
                for new_message in messages:
                    self._add_message(
                        session_id=session_id, 
                        is_user=new_message.role == ChatRole.USER, 
                        message=new_message.message, 
                        tool_calls=new_message.tool_calls
                    )
                
                break
    
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
                
    def get_prompt_generator(
        self,
        session: ChatSession,
        input: str
    ) -> Generator[CompletionChunk, None, List[BaseChatMessage]]:
        p_type = PromptType(session.prompt_type)
        
        messages = self.chat_repository.get_chat_messages(session.id)
        model_messages = self._get_chat_messages(messages)
        
        if p_type == PromptType.LESSON:
            if session.resource_id is None:
                raise ValueError("Resource ID is required for lesson prompt")
            
            lesson = self.course_repository.get_lesson(session.resource_id)
            
            prompt = LessonDiscussionPrompt()
            return prompt.get_responses(
                history=model_messages,
                message=input,
                lesson_content="\n\n".join(
                    [
                        f"{section.title}\n{section.content}" 
                        for section in lesson.sections
                    ]
                )
            )
            
        raise ValueError("Invalid prompt type")