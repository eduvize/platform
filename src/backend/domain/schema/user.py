from datetime import datetime
from typing import Literal, Optional
from sqlmodel import Field, Relationship, SQLModel
import domain.schema.curriculum as curriculum
from domain.schema.profile import UserProfileFrontend, UserProfileBackend, UserProfileDatabase, UserProfileDevops
from domain.schema.profile import UserProfileHobby, UserProfileStudent, UserProfileProfessional
import uuid

UserIdentifiers = Literal["id", "username", "email", "verification_code"]
UserIncludes = Literal["profile", "skills", "curriculums", "reviews", "enrollments", "chat_sessions"]

class UserBase(SQLModel):
    username: str                           = Field(unique=True)
    email: str                              = Field(unique=True)
    pending_verification: bool              = Field(default=True, nullable=False)
    verification_code: Optional[str]
    created_at_utc: datetime            = Field(nullable=False, default_factory=datetime.utcnow)

class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str                  = Field(nullable=False)
    verification_code: Optional[str]    = Field()
    verification_sent_at_utc: datetime  = Field(default_factory=datetime.utcnow)
    
    last_login_at_utc: datetime         = Field(default_factory=datetime.utcnow)
    
    profile: "UserProfile"                                              = Relationship(back_populates="user")
    curriculums: list["UserCurriculum"]                                 = Relationship(back_populates="user")
    curriculum_reviews: list["curriculum.CurriculumReview"]             = Relationship(back_populates="user")
    curriculum_enrollments: list["curriculum.CurriculumEnrollment"]     = Relationship(back_populates="user")

class UserProfileBase(SQLModel):
    first_name: Optional[str]                           = Field()
    last_name: Optional[str]                            = Field()
    bio: Optional[str]                                  = Field()
    github_username: Optional[str]                      = Field()
    avatar_url: Optional[str]                           = Field()
    

class UserProfile(UserProfileBase, table=True):
    __tablename__ = "user_profiles"
    
    id: uuid.UUID                                       = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID                                  = Field(default=None, foreign_key="users.id")
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

class UserCurriculumBase(SQLModel):
    curriculum_id: uuid.UUID                = Field(default=None, foreign_key="curriculums.id")
    current_lesson_id: Optional[uuid.UUID]  = Field(default=None, foreign_key="curriculum_lessons.id")

class UserCurriculum(UserCurriculumBase, table=True):
    __tablename__ = "user_curriculums"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID                      = Field(default=None, foreign_key="users.id")
    instructor_notes: Optional[str]         = Field()
    
    user: User                              = Relationship(back_populates="curriculums")