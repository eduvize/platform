import uuid
import domain.schema.user as user
from sqlmodel import Field, Relationship, SQLModel

class UserProfileProfessionalBase(SQLModel):
    user_profile_id: uuid.UUID                          = Field(default=None, foreign_key="user_profiles.id")

class UserProfileProfessional(UserProfileProfessionalBase, table=True):
    __tablename__ = "user_profiles_professional"
    
    id: uuid.UUID                                       = Field(default_factory=uuid.uuid4, primary_key=True)
    skills: list["UserProfileProfessionalSkill"]        = Relationship(back_populates="user_profile_professional")
    user_profile: "user.UserProfile"                    = Relationship(back_populates="professional")
    
class UserProfileProfessionalSkillBase(SQLModel):
    skill_id: uuid.UUID                                 = Field(nullable=False, foreign_key="user_profiles_skills.id")
    
class UserProfileProfessionalSkill(UserProfileProfessionalSkillBase, table=True):
    __tablename__ = "user_profiles_professional_skills"
    
    id: uuid.UUID                                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_professional_id: uuid.UUID                 = Field(default=None, foreign_key="user_profiles_professional.id")
    
    user_profile_professional: "UserProfileProfessional"    = Relationship(back_populates="skills")
    
class UserProfileStudentBase(SQLModel):
    user_profile_id: uuid.UUID                              = Field(default=None, foreign_key="user_profiles.id")
    
class UserProfileStudent(UserProfileStudentBase, table=True):
    __tablename__ = "user_profiles_student"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    skills: list["UserProfileStudentSkill"]         = Relationship(back_populates="user_profile_student")
    user_profile: "user.UserProfile"                = Relationship(back_populates="student")
    
class UserProfileStudentSkillBase(SQLModel):
    skill_id: uuid.UUID                             = Field(nullable=False, foreign_key="user_profiles_skills.id")
    
class UserProfileStudentSkill(UserProfileStudentSkillBase, table=True):
    __tablename__ = "user_profiles_student_education_skills"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_student_id: uuid.UUID              = Field(default=None, foreign_key="user_profiles_student.id")
    
    user_profile_student: "UserProfileStudent"      = Relationship(back_populates="skills")