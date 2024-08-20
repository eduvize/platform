import logging
import json
import uuid
from typing import List, Optional

from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from domain.schema.chat import ChatMessage, ChatSession, ChatToolCall
from common.database import engine

logger = logging.getLogger("ChatRepository")

class ChatRepository:    
    def add_chat_message(
        self, 
        session_id: uuid.UUID,
        is_user: bool,
        content: Optional[str]
    ) -> ChatMessage:
        """
        Adds a message to a chat session

        Args:
            user_id (str): The user that owns the chat session
            message_dto (ChatMessageDto): The message to add

        Returns:
            ChatMessage: The added message
        """
        
        with Session(engine) as session:
            chat_message = ChatMessage(
                session_id=session_id,
                is_user=is_user,
                content=content
            )
            session.add(chat_message)
            session.commit()
            session.refresh(chat_message)
            
            return chat_message
        
    def add_tool_message(
        self,
        message_id: uuid.UUID,
        call_id: str,
        tool_name: str,
        arguments: str,
        result: str
    ):
        with Session(engine) as session:
            tool_call = ChatToolCall(
                message_id=message_id,
                tool_call_id=call_id,
                tool_name=tool_name,
                json_arguments=arguments,
                result=result
            )
            session.add(tool_call)
            session.commit()
        
    def get_chat_messages(
        self,
        session_id: uuid.UUID
    ) -> List[ChatMessage]:
        """
        Gets all messages in a chat session

        Args:
            user_id (uuid.UUID): The user that owns the chat session
            session_id (uuid.UUID): The chat session to get messages for

        Returns:
            List[ChatMessage]: The messages in the chat session
        """
        
        logger.info(f"Getting chat messages for session {session_id}")
        
        with Session(engine) as session:
            query = select(ChatMessage).where(
                ChatMessage.session_id == session_id
            )
            
            query = query.options(joinedload(ChatMessage.tool_calls))
            
            # Order by created_at_utc descending
            query = query.order_by(ChatMessage.created_at_utc.desc())
            query = query.limit(50)
            
            messages = session.exec(query).unique().all()
            messages.reverse()
            
            return messages
    
    def get_session_by_curriculum(
        self,
        user_id: uuid.UUID,
        curriculum_id: uuid.UUID
    ) -> uuid.UUID:
        """
        Gets the chat session for a user and given curriculum

        Args:
            user_id (uuid.UUID): The user to get the session for
            curriculum_id (uuid.UUID): The curriculum to get the session for
        
        Returns:
            Optional[uuid.UUID]: The ID of the chat session or None
        """
        
        with Session(engine) as session:
            query = select(ChatSession).where(
                ChatSession.user_id == user_id,
                ChatSession.curriculum_id == curriculum_id
            )
        
            result = session.exec(query).first()
            
            if result:
                return result.id
            else:
                # Create a new session if one does not exist
                logger.info(f"Creating new chat session for user {user_id} and curriculum {curriculum_id}")
                chat_session = ChatSession(
                    user_id=user_id,
                    curriculum_id=curriculum_id
                )
                session.add(chat_session)
                session.commit()
                session.refresh(chat_session)
                
                logger.info(f"Created new chat session with ID {chat_session.id}")
                
                return chat_session.id
        
    def get_session_by_lesson(
        self,
        user_id: uuid.UUID,
        lesson_id: uuid.UUID
    ) -> uuid.UUID:
        """
        Gets the chat session for a user and given lesson

        Args:
            user_id (uuid.UUID): The user to get the session for
            lesson_id (uuid.UUID): The lesson to get the session for

        Returns:
            Optional[uuid.UUID]: The ID of the chat session or None
        """
        
        with Session(engine) as session:
            query = select(ChatSession).where(
                ChatSession.user_id == user_id,
                ChatSession.lesson_id == lesson_id
            )
        
            result = session.exec(query).first()
            
            if result:
                return result.id
            else:
                # Create a new session if one does not exist
                logger.info(f"Creating new chat session for user {user_id} and lesson {lesson_id}")
                chat_session = ChatSession(
                    user_id=user_id,
                    lesson_id=lesson_id
                )
                session.add(chat_session)
                session.commit()
                session.refresh(chat_session)
                
                logger.info(f"Created new chat session with ID {chat_session.id}")
                
                return chat_session.id
            
    def get_session_by_exercise(
        self,
        user_id: uuid.UUID,
        exercise_id: uuid.UUID
    ) -> uuid.UUID:
        """
        Gets the chat session for a user and given exercise

        Args:
            user_id (uuid.UUID): The user to get the session for
            exercise_id (uuid.UUID): The exercise to get the session for

        Returns:
            Optional[uuid.UUID]: The ID of the chat session or None
        """
        
        with Session(engine) as session:
            query = select(ChatSession).where(
                ChatSession.user_id == user_id,
                ChatSession.exercise_id == exercise_id
            )
        
            result = session.exec(query).first()
            
            if result:
                return result.id
            else:
                # Create a new session if one does not exist
                logger.info(f"Creating new chat session for user {user_id} and exercise {exercise_id}")
                chat_session = ChatSession(
                    user_id=user_id,
                    exercise_id=exercise_id
                )
                session.add(chat_session)
                session.commit()
                session.refresh(chat_session)
                
                logger.info(f"Created new chat session with ID {chat_session.id}")
                
                return chat_session.id
            
    def get_default_session(
        self,
        user_id: uuid.UUID
    ) -> uuid.UUID:
        """
        Gets the default chat session for a user

        Args:
            user_id (uuid.UUID): The user to get the session for

        Returns:
            Optional[uuid.UUID]: The ID of the chat session or None
        """
        
        logger.info(f"Getting default chat session for user {user_id}")
        
        with Session(engine) as session:
            query = select(ChatSession).where(
                ChatSession.user_id == user_id,
                ChatSession.curriculum_id == None,
                ChatSession.lesson_id == None,
                ChatSession.exercise_id == None
            )
        
            result = session.exec(query).first()
            
            if result:
                return result.id
            else:
                # Create a new session if one does not exist
                logger.info(f"Creating new default chat session for user {user_id}")
                chat_session = ChatSession(
                    user_id=user_id
                )
                session.add(chat_session)
                session.commit()
                session.refresh(chat_session)
                
                logger.info(f"Created new chat session with ID {chat_session.id}")
                
                return chat_session.id