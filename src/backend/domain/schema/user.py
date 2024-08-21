from datetime import datetime
from typing import Literal, Optional
from sqlmodel import Field, Relationship, SQLModel
import domain.schema.courses as courses
import domain.schema.instructor as instructor
from domain.schema.profile import UserProfileHobby, UserProfileStudent, UserProfileProfessional
import uuid

UserIdentifiers = Literal["id", "username", "email", "verification_code"]
UserIncludes = Literal["profile", "instructor"]

class UserBase(SQLModel):
    username: str                           = Field(unique=True)
    email: str                              = Field(unique=True)
    pending_verification: bool              = Field(default=True, nullable=False)
    verification_code: Optional[str]
    created_at_utc: datetime            = Field(nullable=False, default_factory=datetime.utcnow)

class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str                  = Field(nullable=True)
    verification_code: Optional[str]    = Field()
    verification_sent_at_utc: datetime  = Field(default_factory=datetime.utcnow)
    
    last_login_at_utc: datetime         = Field(default_factory=datetime.utcnow)
    
    profile: "UserProfile"                          = Relationship(back_populates="user")
    external_auth: Optional["UserExternalAuth"]     = Relationship(back_populates="user")
    instructor: Optional["instructor.Instructor"]   = Relationship(back_populates="user")
    courses: list["courses.Course"]                 = Relationship(back_populates="user")
    
class UserExternalAuth(SQLModel, table=True):
    __tablename__ = "users_external_auth"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID                  = Field(default=None, foreign_key="users.id")
    provider_id: str                    = Field(nullable=False)
    external_id: str                    = Field(nullable=False)
    created_at_utc: datetime            = Field(default_factory=datetime.utcnow)
    
    user: User                          = Relationship(back_populates="external_auth")

class UserProfileBase(SQLModel):
    first_name: Optional[str]                           = Field()
    last_name: Optional[str]                            = Field()
    birthdate: Optional[datetime]                       = Field()
    bio: Optional[str]                                  = Field()
    github_username: Optional[str]                      = Field()
    avatar_url: Optional[str]                           = Field()

class UserProfile(UserProfileBase, table=True):
    __tablename__ = "user_profiles"
    
    id: uuid.UUID                                       = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID                                  = Field(default=None, foreign_key="users.id")
    last_updated_at_utc: datetime                       = Field(default_factory=datetime.utcnow, nullable=False)
    
    disciplines: list["UserProfileDiscipline"]          = Relationship(back_populates="user_profile")
    skills: list["UserProfileSkill"]                    = Relationship(back_populates="user_profile")
    
    hobby: Optional["UserProfileHobby"]                 = Relationship(back_populates="user_profile")
    student: Optional["UserProfileStudent"]             = Relationship(back_populates="user_profile")
    professional: Optional["UserProfileProfessional"]   = Relationship(back_populates="user_profile")
    
    user: User                                          = Relationship(back_populates="profile")
    
class UserProfileDisciplineBase(SQLModel):
    discipline_type: int            = Field(nullable=False)
    proficiency: Optional[int]      = Field(default=None)
    notes: Optional[str]            = Field()
    
class UserProfileDiscipline(UserProfileDisciplineBase, table=True):
    __tablename__ = "user_profiles_disciplines"
    
    id: uuid.UUID                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID      = Field(default=None, foreign_key="user_profiles.id")
    
    user_profile: UserProfile       = Relationship(back_populates="disciplines")

class UserProfileSkillBase(SQLModel):
    skill_type: int                 = Field(nullable=False)
    skill: str                      = Field(nullable=False)
    proficiency: Optional[int]      = Field(0)
    notes: Optional[str]            = Field()

class UserProfileSkill(UserProfileSkillBase, table=True):
    __tablename__ = "user_profiles_skills"
    
    id: uuid.UUID                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID      = Field(default=None, foreign_key="user_profiles.id")
    
    user_profile: UserProfile      = Relationship(back_populates="skills")    