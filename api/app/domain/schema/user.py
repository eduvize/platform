from typing import Literal
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from ...common.database import Context
import uuid

UserIdentifiers = Literal["id", "username", "email", "verification_code"]
UserIncludes = Literal["profile", "skills", "curriculums", "reviews", "enrollments", "chat_sessions"]

class User(Context):
    __tablename__ = "users"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username                    = Column(Text, nullable=False, unique=True)
    email                       = Column(Text, nullable=False, unique=True)
    password_hash               = Column(Text, nullable=False)
    
    pending_verification        = Column(Boolean, nullable=False, default=True)
    verification_code           = Column(Text)
    verification_sent_at_utc    = Column(TIMESTAMP)
    
    created_at_utc              = Column(TIMESTAMP, nullable=False, default='now()')
    last_login_at_utc           = Column(TIMESTAMP)
    
    profile                     = relationship("UserProfile", back_populates="user", uselist=False)
    skills                      = relationship("UserSkill", back_populates="user")
    curriculums                 = relationship("UserCurriculum", back_populates="user")
    reviews                     = relationship("CurriculumReview", back_populates="user")
    enrollments                 = relationship("CurriculumEnrollment", back_populates="user")
    chat_sessions               = relationship("ChatSession", back_populates="user")

class UserProfile(Context):
    __tablename__ = "user_profiles"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id                     = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    first_name                  = Column(Text)
    last_name                   = Column(Text)
    bio                         = Column(Text)
    github_username             = Column(Text)
    avatar_url                  = Column(Text)
    last_updated_at_utc         = Column(TIMESTAMP, nullable=False, default='now()')
    
    user                        = relationship("User", back_populates="profile", uselist=False)
    frontend                    = relationship("UserProfileFrontend", uselist=False, lazy="joined", backref="user_profiles")
    backend                     = relationship("UserProfileBackend", uselist=False, lazy="joined", backref="user_profiles")
    database                    = relationship("UserProfileDatabase", uselist=False, lazy="joined", backref="user_profiles")
    devops                      = relationship("UserProfileDevops", uselist=False, lazy="joined", backref="user_profiles")
    
    hobby                       = relationship("UserProfileHobby", uselist=False, lazy="joined", backref="user_profiles")
    student                     = relationship("UserProfileStudent", uselist=False, lazy="joined", backref="user_profiles")
    professional                = relationship("UserProfileProfessional", uselist=False, lazy="joined", backref="user_profiles")

class UserSkill(Context):
    __tablename__ = "user_skills"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id                     = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    skill_type                  = Column(Integer, nullable=False)
    skill                       = Column(Text, nullable=False)
    proficiency                 = Column(Integer, nullable=False)
    notes                       = Column(Text)
    created_at_utc              = Column(TIMESTAMP, nullable=False, default='now()')
    
    user                        = relationship("User", back_populates="skills", uselist=False)
    
class UserCurriculum(Context):
    __tablename__ = "user_curriculums"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id                     = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    curriculum_id               = Column(PG_UUID(as_uuid=True), ForeignKey("curriculums.id"), nullable=False)
    instructor_notes            = Column(Text)
    current_lesson_id           = Column(PG_UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    
    user                        = relationship("User", back_populates="curriculums", uselist=False)