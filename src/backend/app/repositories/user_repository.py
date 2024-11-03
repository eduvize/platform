from datetime import datetime
from typing import List, Optional, Union
from sqlalchemy import UUID
from sqlalchemy.orm import joinedload
from sqlmodel import select
from domain.schema.user import User, UserExternalAuth, UserIdentifiers
from domain.schema.instructors import Instructor
from common.database import get_async_session

class UserRepository:
    """
    Handles all primary data access for user records in the database
    """
    async def create_user(
        self, 
        email_address: str, 
        username: str, 
        password_hash: Optional[str],
        set_email_validated: bool = False
    ) -> User:
        """
        Creates a new user record in the database

        Args:
            email_address (str): The user's email address
            username (str): The unique name for the user
            password_hash (str): A hash derived from the user's password
            set_email_validated (bool): Whether to set the email as validated

        Returns:
            User: The newly created user record
        """
        user = User(
            email=email_address, 
            username=username, 
            password_hash=password_hash,
            pending_verification=not set_email_validated
        )
        
        async for session in get_async_session():
            # Get the first instructor (TODO: Let them choose)
            instructor_query = select(Instructor).order_by(Instructor.id).limit(1)
            result = await session.exec(instructor_query)
            instructor = result.one_or_none()
            
            if instructor is None:
                raise Exception("No instructor found")
            
            user.default_instructor_id = instructor.id
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
        
        return user
    
    async def create_external_auth(self, user_id: UUID, provider: str, external_id: str):
        """
        Creates a new external authentication record for a user

        Args:
            user_id (UUID): The ID of the user to associate the external auth with
            provider (str): The provider of the external authentication
            external_id (str): The ID of the user on the external provider
        """
        async for session in get_async_session():
            user_query = select(User).where(User.id == user_id)
            result = await session.exec(user_query)
            user = result.one_or_none()
            
            if user is None:
                return None
            
            user.external_auth = UserExternalAuth(
                provider_id=provider, 
                external_id=external_id
            )
            
            await session.commit()
            
    async def set_avatar_url(self, user_id: UUID, avatar_url: str) -> None:
        """
        Sets the avatar URL for a user

        Args:
            user_id (UUID): The ID of the user to set the avatar for
            avatar_url (str): The URL of the avatar
        """
        async for session in get_async_session():
            query = select(User).where(User.id == user_id)
            result = await session.exec(query)
            
            user = result.one_or_none()
            
            if user:
                user.profile_photo_url = avatar_url
            
            await session.commit()
            
    async def set_default_instructor(self, user_id: UUID, instructor_id: UUID) -> None:
        """
        Sets the default instructor for a user
        """
        async for session in get_async_session():
            query = select(User).where(User.id == user_id)
            result = await session.exec(query)
            
            user = result.one_or_none()
            if user:
                user.default_instructor_id = instructor_id
                await session.commit()
    
    async def get_user(self, by: UserIdentifiers, value: Union[str, UUID]) -> Optional[User]:
        """
        Retrieves a user by one of their unique identifiers

        Args:
            by (UserIdentifiers): The type of identifier to search by
            value (Union[str, UUID]): The value of the identifier

        Returns:
            Optional[User]: The user record if found, otherwise None
        """
        async for session in get_async_session():
            query = select(User)
            if by == "id":
                query = query.where(User.id == value)
            elif by == "username":
                query = query.where(User.username == value)
            elif by == "email":
                query = query.where(User.email == value)
            elif by == "verification_code":
                query = query.where(
                    User.verification_code == value,
                    User.pending_verification == True,
                    User.verification_code.is_not(None)
                )

            # Join the external auth
            query = query.options(joinedload(User.external_auth))
            
            result = await session.exec(query)
            record = result.unique().one_or_none()
            
            return record
        
    async def set_verification_code(self, user_id: UUID, code: str) -> None:
        """
        Sets the verification code for a user

        Args:
            user_id (UUID): The ID of the user to set the code for
            code (str): The verification code to set
        """
        async for session in get_async_session():
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            
            user = result.scalar_one_or_none()
            if user:
                user.pending_verification = True
                user.verification_sent_at_utc = datetime.utcnow()
                user.verification_code = code
            
                await session.commit()
            
    async def mark_verified(self, user_id: UUID) -> None:
        """
        Marks a user as verified

        Args:
            user_id (UUID): The ID of the user to mark
        """
        async for session in get_async_session():
            query = select(User).where(User.id == user_id)
            result = await session.exec(query)
            
            user = result.one_or_none()
            if user:
                user.pending_verification = False
                user.verification_code = None
            
                await session.commit()
                
    async def set_onboarding_session_id(self, user_id: UUID, session_id: UUID) -> None:
        """
        Sets the onboarding session ID for a user
        """
        async for session in get_async_session():
            query = select(User).where(User.id == user_id)
            result = await session.exec(query)
            
            user = result.one_or_none()
            if user:
                user.onboarding_session_id = session_id
                await session.commit()
