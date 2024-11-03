from datetime import datetime
from typing import Literal, Optional
from sqlmodel import Field, Relationship, SQLModel
import domain.schema as schema
import uuid

UserIdentifiers = Literal["id", "username", "email", "verification_code"]

class UserBase(SQLModel):
    username: str                               = Field(unique=True)
    email: str                                  = Field(unique=True)
    pending_verification: bool                  = Field(default=True, nullable=False)
    default_instructor_id: Optional[uuid.UUID] = Field(nullable=True)
    profile_photo_url: str                     = Field(nullable=True)
    created_at_utc: datetime                    = Field(nullable=False, default_factory=datetime.utcnow)

class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str                  = Field(nullable=True)
    verification_code: Optional[str]    = Field()
    verification_sent_at_utc: datetime  = Field(default_factory=datetime.utcnow)
    onboarding_session_id: Optional[uuid.UUID] = Field(nullable=True, foreign_key="chat_sessions.id")
    
    last_login_at_utc: datetime         = Field(default_factory=datetime.utcnow)
    
    external_auth: Optional["UserExternalAuth"]                     = Relationship(back_populates="user")
    courses: list["schema.courses.course.Course"]                   = Relationship(back_populates="user")
    
class UserExternalAuth(SQLModel, table=True):
    __tablename__ = "users_external_auth"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID                  = Field(default=None, foreign_key="users.id")
    provider_id: str                    = Field(nullable=False)
    external_id: str                    = Field(nullable=False)
    created_at_utc: datetime            = Field(default_factory=datetime.utcnow)
    
    user: User                          = Relationship(back_populates="external_auth")