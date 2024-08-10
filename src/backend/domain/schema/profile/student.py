from typing import Optional
import uuid
import domain
from sqlmodel import SQLModel, Field, Relationship

class UserProfileStudentBase(SQLModel):
    pass

class UserProfileStudent(UserProfileStudentBase, table=True):
    __tablename__ = "user_profiles_student"
    
    id: uuid.UUID                                       = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID                          = Field(default=None, foreign_key="user_profiles.id")
    
    schools: list["UserProfileSchool"]                  = Relationship(back_populates="user_profile_student")
    user_profile: "domain.schema.user.UserProfile"      = Relationship(back_populates="student")

class UserProfileSchoolBase(SQLModel):
    school_name: str                            = Field(nullable=False)
    focus: Optional[str]                        = Field(default=None)
    
    user_profile_student_id: uuid.UUID          = Field(default=None, foreign_key="user_profiles_student.id")

class UserProfileSchool(UserProfileSchoolBase, table=True):
    __tablename__ = "user_profiles_schools"
    
    id: uuid.UUID                               = Field(default_factory=uuid.uuid4, primary_key=True)
    
    skills: list["UserProfileSchoolSkill"]      = Relationship(back_populates="user_profile_school")
    
    user_profile_student: "UserProfileStudent"  = Relationship(back_populates="schools")
    
class UserProfileSchoolSkillBase(SQLModel):
    skill_id: uuid.UUID                     = Field(nullable=False, foreign_key="user_profiles_skills.id")

class UserProfileSchoolSkill(UserProfileSchoolSkillBase, table=True):
    __tablename__ = "user_profiles_schools_skills"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_school_id: uuid.UUID        = Field(default=None, foreign_key="user_profiles_schools.id")
    
    user_profile_school: "UserProfileSchool"  = Relationship(back_populates="skills")