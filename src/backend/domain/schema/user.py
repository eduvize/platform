from datetime import datetime
from typing import Literal, Optional
from sqlmodel import Field, Relationship, SQLModel
import domain.schema.curriculum as curriculum
from domain.schema.profile import UserProfileFrontend, UserProfileBackend, UserProfileDatabase, UserProfileDevops
from domain.schema.profile import UserProfileHobby, UserProfileStudent, UserProfileProfessional
from domain.dto.profile.disciplines import UserProfileBackend, UserProfileFrontend
import uuid

UserIdentifiers = Literal["id", "username", "email", "verification_code"]
UserIncludes = Literal["profile", "skills", "curriculums", "reviews", "enrollments", "chat_sessions"]

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str                       = Field(unique=True)
    email: str                          = Field(unique=True)
    password_hash: str                  = Field(nullable=False)
    
    pending_verification: bool          = Field(default=True, nullable=False)
    verification_code: Optional[str]    = Field()
    verification_sent_at_utc: datetime  = Field(default_factory=datetime.utcnow)
    
    created_at_utc: datetime            = Field(nullable=False, default_factory=datetime.utcnow)
    last_login_at_utc: datetime         = Field(default_factory=datetime.utcnow)
    
    profile: "UserProfile"                                              = Relationship(back_populates="user")
    curriculums: list["UserCurriculum"]                                 = Relationship(back_populates="user")
    curriculum_reviews: list["curriculum.CurriculumReview"]             = Relationship(back_populates="user")
    curriculum_enrollments: list["curriculum.CurriculumEnrollment"]     = Relationship(back_populates="user")

class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"
    
    id: uuid.UUID                                       = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID                                  = Field(default=None, foreign_key="users.id")
    first_name: Optional[str]                           = Field()
    last_name: Optional[str]                            = Field()
    bio: Optional[str]                                  = Field()
    github_username: Optional[str]                      = Field()
    avatar_url: Optional[str]                           = Field()
    last_updated_at_utc: datetime                       = Field(default_factory=datetime.utcnow, nullable=False)
    
    frontend: Optional["UserProfileFrontend"]           = Relationship(back_populates="user_profile")
    backend: Optional["UserProfileBackend"]             = Relationship(back_populates="user_profile")
    database: Optional["UserProfileDatabase"]           = Relationship(back_populates="user_profile")
    devops: Optional["UserProfileDevops"]               = Relationship(back_populates="user_profile")
    
    skills: list["UserProfileSkill"]                    = Relationship(back_populates="user_profile")
    
    hobby: Optional["UserProfileHobby"]                 = Relationship(back_populates="user_profile")
    student: Optional["UserProfileStudent"]             = Relationship(back_populates="user_profile")
    professional: Optional["UserProfileProfessional"]   = Relationship(back_populates="user_profile")
    
    user: User                                          = Relationship(back_populates="profile")

class UserProfileSkill(SQLModel, table=True):
    __tablename__ = "user_profiles_skills"
    
    id: uuid.UUID                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID              = Field(default=None, foreign_key="users.id")
    user_profile_id: uuid.UUID      = Field(default=None, foreign_key="user_profiles.id")
    skill_type: int                 = Field(nullable=False)
    skill: str                      = Field(nullable=False)
    proficiency: Optional[int]      = Field(0)
    notes: Optional[str]            = Field()
    created_at_utc: datetime        = Field(default_factory=datetime.utcnow, nullable=False)
    
    user_profile: UserProfile      = Relationship(back_populates="skills")    

class UserCurriculum(SQLModel, table=True):
    __tablename__ = "user_curriculums"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID                      = Field(default=None, foreign_key="users.id")
    curriculum_id: uuid.UUID                = Field(default=None, foreign_key="curriculums.id")
    instructor_notes: Optional[str]         = Field()
    current_lesson_id: Optional[uuid.UUID]  = Field(default=None, foreign_key="curriculum_lessons.id")
    
    user: User                              = Relationship(back_populates="curriculums")