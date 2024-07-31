from typing import List, Literal, Optional, Union
from sqlalchemy import UUID
from sqlalchemy.orm import joinedload
from ..common.database import get_session
from ..models.schema.user import User

INCLUDE_FIELDS = List[
    Literal["profile", "skills", "curriculums", "reviews", "enrollments", "chat_sessions"]
]

SELECT_BY = Literal["name", "id", "email"]

class UserRepository:
    def create_user(self, email_address: str, username: str, password_hash: str) -> User:
        user = User(email=email_address, username=username, password_hash=password_hash)
        
        with get_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        
        return user
    
    def get_user(self, by: SELECT_BY, value: Union[str, UUID], include: Optional[INCLUDE_FIELDS]) -> Optional[User]:
        with get_session() as session:
            if by == "id":
                query = session.query(User).filter(User.id == value)
            elif by == "name":
                query = session.query(User).filter(User.username == value)
            elif by == "email":
                query = session.query(User).filter(User.email == value)
            
            if include:
                for field in include:
                    query = query.options(joinedload(getattr(User, field)))
        
            return query.first()