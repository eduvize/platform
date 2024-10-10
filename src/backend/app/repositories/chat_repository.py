import logging
import json
import uuid
from typing import List, Optional

from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from domain.schema.chat import ChatMessage, ChatSession, ChatToolCall
from common.database import async_engine

logger = logging.getLogger("ChatRepository")

class ChatRepository:
    async def create_chat_session(
        self,
        user_id: uuid.UUID,
        instructor_id: uuid.UUID,
        prompt_type: str,
        resource_id: Optional[uuid.UUID] = None
    ) -> ChatSession:
        """
        Creates a new chat session

        Args:
            user_id (uuid.UUID): The user that owns the chat session
            prompt_type (str): The type of prompt for this session
            resource_id (Optional[uuid.UUID]): The associated resource ID, if any

        Returns:
            ChatSession: The created chat session
        """
        
        async with AsyncSession(async_engine) as session:
            chat_session = ChatSession(
                user_id=user_id,
                instructor_id=instructor_id,
                prompt_type=prompt_type,
                resource_id=resource_id
            )
            session.add(chat_session)
            await session.commit()
            await session.refresh(chat_session)
            
            return chat_session
    
    async def add_chat_message(
        self, 
        session_id: uuid.UUID,
        sender_id: uuid.UUID,
        is_user: bool,
        content: Optional[str]
    ) -> ChatMessage:
        """
        Adds a message to a chat session

        Args:
            session_id (uuid.UUID): The ID of the chat session
            is_user (bool): Whether the message is from the user
            content (Optional[str]): The content of the message

        Returns:
            ChatMessage: The added message
        """
        
        async with AsyncSession(async_engine) as session:
            chat_message = ChatMessage(
                session_id=session_id,
                is_user=is_user,
                content=content,
                instructor_id=sender_id if not is_user else None,
                user_id=sender_id if is_user else None
            )
            session.add(chat_message)
            await session.commit()
            await session.refresh(chat_message)
            
            return chat_message
        
    async def add_tool_message(
        self,
        message_id: uuid.UUID,
        call_id: str,
        tool_name: str,
        arguments: str,
        result: str
    ) -> None:
        """
        Adds a tool message to a chat message

        Args:
            message_id (uuid.UUID): The ID of the associated chat message
            call_id (str): The ID of the tool call
            tool_name (str): The name of the tool
            arguments (str): The arguments passed to the tool
            result (str): The result of the tool call
        """
        async with AsyncSession(async_engine) as session:
            tool_call = ChatToolCall(
                message_id=message_id,
                tool_call_id=call_id,
                tool_name=tool_name,
                json_arguments=arguments,
                result=result
            )
            session.add(tool_call)
            await session.commit()
        
    async def get_session(
        self,
        session_id: uuid.UUID
    ) -> Optional[ChatSession]:
        """
        Gets a chat session by ID
        
        Args:
            session_id (uuid.UUID): The ID of the chat session to get
            
        Returns:
            Optional[ChatSession]: The chat session, if found
        """
        
        async with AsyncSession(async_engine) as session:
            query = select(ChatSession).where(ChatSession.id == session_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
    async def get_chat_messages(
        self,
        session_id: uuid.UUID
    ) -> List[ChatMessage]:
        """
        Gets all messages in a chat session

        Args:
            session_id (uuid.UUID): The chat session to get messages for

        Returns:
            List[ChatMessage]: The messages in the chat session
        """
        
        logger.info(f"Getting chat messages for session {session_id}")
        
        async with AsyncSession(async_engine) as session:
            query = select(ChatMessage).where(
                ChatMessage.session_id == session_id
            )
            
            query = query.options(joinedload(ChatMessage.tool_calls))
            
            # Order by created_at_utc descending
            query = query.order_by(ChatMessage.created_at_utc.desc())
            query = query.limit(50)
            
            result = await session.execute(query)
            messages = result.scalars().unique().all()
            messages.reverse()
            
            return messages