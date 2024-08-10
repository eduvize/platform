import uuid
import domain
from sqlmodel import SQLModel, Field, Relationship

class UserProfileProfessionalBase(SQLModel):
    pass

class UserProfileProfessional(UserProfileProfessionalBase, table=True):
    __tablename__ = "user_profiles_professional"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID                      = Field(default=None, foreign_key="user_profiles.id")
    
    employers: list["UserProfileEmployment"]        = Relationship(back_populates="user_profile_professional")

    user_profile: "domain.schema.user.UserProfile"  = Relationship(back_populates="professional")

class UserProfileEmploymentBase(SQLModel):
    company_name: str                                       = Field(nullable=False)
    position: str                                           = Field(nullable=False)
    description: str                                        = Field(nullable=False)
    is_current: bool                                        = Field(default=False)
    

class UserProfileEmployment(UserProfileEmploymentBase, table=True):
    __tablename__ = "user_profiles_employment"
    
    id: uuid.UUID                                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_professional_id: uuid.UUID                 = Field(default=None, foreign_key="user_profiles_professional.id")
    skills: list["UserProfileEmploymentSkill"]              = Relationship(back_populates="user_profile_employment")
    user_profile_professional: "UserProfileProfessional"    = Relationship(back_populates="employers")
    
class UserProfileEmploymentSkillBase(SQLModel):
    skill_id: uuid.UUID                                     = Field(foreign_key="user_profiles_skills.id")
    
class UserProfileEmploymentSkill(UserProfileEmploymentSkillBase, table=True):
    __tablename__ = "user_profiles_employment_skills"
    
    id: uuid.UUID                                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_employment_id: uuid.UUID                   = Field(foreign_key="user_profiles_employment.id")
    user_profile_employment: "UserProfileEmployment"        = Relationship(back_populates="skills")