from typing import List, Literal, Optional, Union
from sqlalchemy import UUID
from sqlalchemy.orm import joinedload
from ..common.database import get_session
from ..models.schema.user import User, UserIdentifiers, UserIncludes, UserProfile

class UserRepository:
    """
    Handles all primary data access for user records in the database
    """
    async def create_user(self, email_address: str, username: str, password_hash: str) -> User:
        """
        Creates a new ueer record in the database

        Args:
            email_address (str): The user's email address
            username (str): The unique name for the user
            password_hash (str): A hash derived from the user's password

        Returns:
            User: The newly created user record
        """
        user = User(email=email_address, username=username, password_hash=password_hash)
        
        with get_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        
        return user
    
    async def upsert_profile(self, user_id: UUID, profile: UserProfile):
        """
        Creates or replaces a user profile record in the database

        Args:
            user_id (UUID): The ID of the user to associate the profile with
            profile (UserProfile): The profile data to store
        """
        with get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if user is None:
                return None
            
            existing_profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
            if existing_profile:
                profile.id = existing_profile.id
                session.merge(profile)
            else:
                profile.user_id = user_id
                session.add(profile)
                
            session.commit()        
    
    async def get_user(self, by: UserIdentifiers, value: Union[str, UUID], include: Optional[List[UserIncludes]] = []) -> Optional[User]:
        """
        Retrieves a user by one of their unique identifiers, optionally joining related data

        Args:
            by (UserIdentifiers): The type of identifier to search by
            value (Union[str, UUID]): The value of the identifier
            include (Optional[List[UserIncludes]], optional): A list of relationships to populate. Defaults to [].

        Returns:
            Optional[User]: _description_
        """
        with get_session() as session:
            if by == "id":
                query = session.query(User).filter(User.id == value)
            elif by == "username":
                query = session.query(User).filter(User.username == value)
            elif by == "email":
                query = session.query(User).filter(User.email == value)
            
            if include:
                for field in include:
                    query = query.options(joinedload(getattr(User, field)))
        
            return query.first()