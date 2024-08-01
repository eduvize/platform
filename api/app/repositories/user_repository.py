from typing import List, Literal, Optional, Union
from sqlalchemy import UUID
from sqlalchemy.orm import joinedload
from ..common.database import get_session
from ..models.schema.user import User, UserIdentifiers, UserIncludes, UserProfile

class UserRepository:
    async def create_user(self, email_address: str, username: str, password_hash: str) -> User:
        user = User(email=email_address, username=username, password_hash=password_hash)
        
        with get_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        
        return user
    
    async def upsert_profile(self, user_id: UUID, profile: UserProfile):
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