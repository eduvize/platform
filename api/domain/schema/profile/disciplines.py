import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.common.database import Context

class UserProfileFrontend(Context):
    __tablename__ = "user_profiles_frontend"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id             = Column(PG_UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    
class UserProfileBackend(Context):
    __tablename__ = "user_profiles_backend"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id             = Column(PG_UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    
class UserProfileDatabase(Context):
    __tablename__ = "user_profiles_database"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id             = Column(PG_UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    
class UserProfileDevops(Context):
    __tablename__ = "user_profiles_devops"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id             = Column(PG_UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)