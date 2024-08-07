import uuid
import domain.schema.user as user
from sqlmodel import Field, Relationship, SQLModel

class UserProfileProfessionalBase(SQLModel):
    user_profile_id: uuid.UUID                          = Field(default=None, foreign_key="user_profiles.id")

class UserProfileProfessional(UserProfileProfessionalBase, table=True):
    __tablename__ = "user_profiles_professional"
    
    id: uuid.UUID                                       = Field(default_factory=uuid.uuid4, primary_key=True)
    
    user_profile: "user.UserProfile"                    = Relationship(back_populates="professional")
    
class UserProfileStudentBase(SQLModel):
    user_profile_id: uuid.UUID                      = Field(default=None, foreign_key="user_profiles.id")
    
class UserProfileStudent(UserProfileStudentBase, table=True):
    __tablename__ = "user_profiles_student"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)

    user_profile: "user.UserProfile"                = Relationship(back_populates="student")