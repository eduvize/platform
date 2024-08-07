import uuid
import domain.schema.user as user
from sqlmodel import Field, Relationship, SQLModel, ForeignKey

class UserProfileProfessional(SQLModel, table=True):
    __tablename__ = "user_profiles_professional"
    
    id: uuid.UUID                                       = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID                          = Field(default=None, foreign_key="user_profiles.id")
    
    user_profile: "user.UserProfile"                    = Relationship(back_populates="professional")

class UserProfileHobby(SQLModel, table=True):
    __tablename__ = "user_profiles_hobby"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID                      = Field(default=None, foreign_key="user_profiles.id")
    
    user_profile: "user.UserProfile"                = Relationship(back_populates="hobby")
    
class UserProfileStudent(SQLModel, table=True):
    __tablename__ = "user_profiles_student"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    user_profile_id: uuid.UUID                      = Field(default=None, foreign_key="user_profiles.id")

    user_profile: "user.UserProfile"                = Relationship(back_populates="student")