from datetime import datetime
from typing import List, Optional, Union
from sqlalchemy import UUID
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from domain.schema.user import User, UserIdentifiers, UserIncludes, UserProfile
from common.database import engine, recursive_load_options

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
        user.profile = UserProfile()
        
        with Session(engine) as session:
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
        with Session(engine) as session:
            user_query = select(User).where(User.id == user_id).join(User.profile)
            resultset = session.exec(user_query)
            
            user = resultset.first()
            if user is None:
                return None
            
            # Merge the new profile data into the existing profile
            user.profile.sqlmodel_update(profile)
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
        with Session(engine) as session:
            query = select(User)
            if by == "id":
                query = query.where(User.id == value)
            elif by == "username":
                query = query.where(User.username == value)
            elif by == "email":
                query = query.where(User.email == value)
            elif by == "verification_code":
                query = query.where(
                    User.verification_code == value and 
                    User.pending_verification == True and 
                    User.verification_code is not None
                )
            
            if include:
                for field in include:
                    query = query.options(*recursive_load_options(User, field))
        
            resultset = session.exec(query)
            
            return resultset.first()
        
    async def set_verification_code(self, user_id: UUID, code: str) -> None:
        """
        Sets the verification code for a user

        Args:
            user_id (UUID): The ID of the user to set the code for
            code (str): The verification code to set
        """
        with Session(engine) as session:
            query = select(User).where(User.id == user_id)
            resultset = session.exec(query)
            
            user = resultset.first()
            user.pending_verification = True
            user.verification_sent_at_utc = datetime.utcnow()
            user.verification_code = code
            
            session.commit()
            
    async def mark_verified(self, user_id: UUID) -> None:
        """
        Marks a user as verified

        Args:
            user_id (UUID): The ID of the user to mark
        """
        with Session(engine) as session:
            query = select(User).where(User.id == user_id)
            resultset = session.exec(query)
            
            user = resultset.first()
            user.pending_verification = False
            user.verification_code = None
            
            session.commit()