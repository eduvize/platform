from typing import Optional
import uuid
import domain
from sqlmodel import SQLModel, Field, Relationship

class UserProfileHobbyBase(SQLModel):
    pass

class UserProfileHobby(UserProfileHobbyBase, table=True):
    __tablename__ = "user_profiles_hobby"
    
    id: uuid.UUID                                       = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID                          = Field(default=None, foreign_key="user_profiles.id")
    
    reasons: list["UserProfileHobbyReason"]             = Relationship(back_populates="user_profile_hobby")
    projects: list["UserProfileHobbyProject"]           = Relationship(back_populates="user_profile_hobby")
    skills: list["UserProfileHobbySkill"]               = Relationship(back_populates="user_profile_hobby")
    user_profile: "domain.schema.user.UserProfile"      = Relationship(back_populates="hobby")

class UserProfileHobbySkillBase(SQLModel):
    skill_id: uuid.UUID                     = Field(nullable=False, foreign_key="user_profiles_skills.id")

class UserProfileHobbySkill(UserProfileHobbySkillBase, table=True):
    __tablename__ = "user_profiles_hobby_skills"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_hobby_id: uuid.UUID        = Field(default=None, foreign_key="user_profiles_hobby.id")
    
    user_profile_hobby: "UserProfileHobby"  = Relationship(back_populates="skills")

class UserProfileHobbyReasonBase(SQLModel):
    reason: str                             = Field(nullable=False)
    user_profile_hobby_id: uuid.UUID        = Field(default=None, foreign_key="user_profiles_hobby.id")

class UserProfileHobbyReason(UserProfileHobbyReasonBase, table=True):
    __tablename__ = "user_profiles_hobby_reasons"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_hobby: "UserProfileHobby"  = Relationship(back_populates="reasons")
    
class UserProfileHobbyProjectBase(SQLModel):
    project_name: str                       = Field(nullable=False)
    description: str                        = Field(nullable=False)
    purpose: Optional[str]                  = Field()
    user_profile_hobby_id: uuid.UUID        = Field(default=None, foreign_key="user_profiles_hobby.id")
    
class UserProfileHobbyProject(UserProfileHobbyProjectBase, table=True):
    __tablename__ = "user_profiles_hobby_projects"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_hobby: "UserProfileHobby"  = Relationship(back_populates="projects")
