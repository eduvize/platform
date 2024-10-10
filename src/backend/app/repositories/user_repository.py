from datetime import datetime
from typing import List, Optional, Union
from sqlalchemy import UUID
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.dto.profile import UserProfileDto
from domain.mapping import (
    map_hobby_data, 
    delete_hobby_data,
    map_student_data,
    delete_student_data, 
    map_professional_data,
    delete_professional_data,
    map_skill_data, 
    map_discipline_data
)
from domain.schema.user import User, UserExternalAuth, UserIdentifiers, UserProfile, UserProfileHobby, UserProfileProfessional, UserProfileStudent
from app.utilities.database import set_none_for_unavailable_relationships
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
        user.profile = UserProfile()
        
        async for session in get_async_session():
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
            result = await session.execute(user_query)
            
            user = result.scalar_one_or_none()
            if user is None:
                return None
            
            user.external_auth = UserExternalAuth(
                provider_id=provider, 
                external_id=external_id
            )
            
            await session.commit()
    
    async def upsert_profile(self, user_id: UUID, profile: UserProfileDto):
        """
        Creates or replaces a user profile record in the database

        Args:
            user_id (UUID): The ID of the user to associate the profile with
            profile (UserProfile): The profile data to store
        """
        async for session in get_async_session():
            user_query = select(User).where(User.id == user_id).options(joinedload(User.profile))
            result = await session.execute(user_query)
            
            user = result.scalar_one_or_none()
            if user is None:
                return None
            
            user.profile.first_name = profile.first_name
            user.profile.last_name = profile.last_name
            user.profile.bio = profile.bio
            user.profile.github_username = profile.github_username
            user.profile.birthdate = profile.birthdate

            map_discipline_data(session, user.profile, profile.disciplines)
            map_skill_data(session, user.profile, profile.skills)
            
            if profile.hobby:
                map_hobby_data(session, user.profile, profile.hobby)
            elif user.profile.hobby:
                delete_hobby_data(session, user.profile.hobby)
                
            if profile.student:
                map_student_data(session, user.profile, profile.student)
            elif user.profile.student:
                delete_student_data(session, user.profile.student)
                
            if profile.professional:
                map_professional_data(session, user.profile, profile.professional)
            elif user.profile.professional:
                delete_professional_data(session, user.profile.professional)
                
            await session.commit()
            
    async def set_avatar_url(self, user_id: UUID, avatar_url: str) -> None:
        """
        Sets the avatar URL for a user

        Args:
            user_id (UUID): The ID of the user to set the avatar for
            avatar_url (str): The URL of the avatar
        """
        async for session in get_async_session():
            query = select(User).where(User.id == user_id).options(joinedload(User.profile))
            result = await session.execute(query)
            
            user = result.scalar_one_or_none()
            
            if not user or not user.profile:
                return
            
            user.profile.avatar_url = avatar_url
            
            await session.commit()
    
    async def get_user(self, by: UserIdentifiers, value: Union[str, UUID], include: Optional[List[str]] = []) -> Optional[User]:
        """
        Retrieves a user by one of their unique identifiers, optionally joining related data

        Args:
            by (UserIdentifiers): The type of identifier to search by
            value (Union[str, UUID]): The value of the identifier
            include (Optional[List[UserIncludes]], optional): A list of relationships to populate. Defaults to [].

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
            
            # Join the profile with hobbies, professional, student, and skills
            # Load the entire profile with all related data
            query = query.options(
                joinedload(User.profile).joinedload(UserProfile.hobby).joinedload(UserProfileHobby.reasons),
                joinedload(User.profile).joinedload(UserProfile.hobby).joinedload(UserProfileHobby.projects),
                joinedload(User.profile).joinedload(UserProfile.hobby).joinedload(UserProfileHobby.skills),
                joinedload(User.profile).joinedload(UserProfile.professional).joinedload(UserProfileProfessional.employers),
                joinedload(User.profile).joinedload(UserProfile.student).joinedload(UserProfileStudent.schools),
                joinedload(User.profile).joinedload(UserProfile.skills),
                joinedload(User.profile).joinedload(UserProfile.disciplines),
            )
        
            result = await session.execute(query)
            record = result.unique().scalar_one_or_none()
            
            if record:
                set_none_for_unavailable_relationships(record, include)
     
                       
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
            result = await session.execute(query)
            
            user = result.scalar_one_or_none()
            if user:
                user.pending_verification = False
                user.verification_code = None
            
                await session.commit()