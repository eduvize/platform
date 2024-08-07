import uuid
from sqlmodel import Field, Relationship, SQLModel
import domain.schema.user as user

class UserProfileFrontend(SQLModel, table=True):
    __tablename__ = "user_profiles_frontend"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID                      = Field(default=None, foreign_key="user_profiles.id")
    
    user_profile: "user.UserProfile"                = Relationship(back_populates="frontend")
    
class UserProfileBackend(SQLModel, table=True):
    __tablename__ = "user_profiles_backend"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID                      = Field(default=None, foreign_key="user_profiles.id")
    
    user_profile: "user.UserProfile"                = Relationship(back_populates="backend")
    
class UserProfileDatabase(SQLModel, table=True):
    __tablename__ = "user_profiles_database"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID                      = Field(default=None, foreign_key="user_profiles.id")
    
    user_profile: "user.UserProfile"                = Relationship(back_populates="database")
    
class UserProfileDevops(SQLModel, table=True):
    __tablename__ = "user_profiles_devops"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID                      = Field(default=None, foreign_key="user_profiles.id")
    
    user_profile: "user.UserProfile"                = Relationship(back_populates="devops")