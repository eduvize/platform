from typing import List, Literal, Optional, Union
from sqlalchemy.orm import joinedload
from ..common.database import get_session
from ..models.schema.user import User

INCLUDE_FIELDS = List[
    Literal["profile", "skills", "curriculums", "reviews", "enrollments", "chat_sessions"]
]

class UserRepository:
    def get_user_by_name(self, username: str, include: Optional[INCLUDE_FIELDS]) -> Optional[User]:
        with get_session() as session:
            query = session.query(User).filter(User.username == username)
            
            if include:
                for field in include:
                    query = query.options(joinedload(getattr(User, field)))
        
            return query.first()
        
    def get_user_by_id(self, user_id: str, include: Optional[INCLUDE_FIELDS]) -> Union[User]:
        with get_session() as session:
            query = session.query(User).filter(User.id == user_id)
            
            if include:
                for field in include:
                    query = query.options(joinedload(getattr(User, field)))
        
            return query.first()