import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.common.database import Context

class UserProfileHobby(Context):
    __tablename__ = "user_profiles_hobby"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id             = Column(PG_UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    
class UserProfileStudent(Context):
    __tablename__ = "user_profiles_student"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id             = Column(PG_UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    
class UserProfileProfessional(Context):
    __tablename__ = "user_profiles_professional"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id             = Column(PG_UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)