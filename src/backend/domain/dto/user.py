import uuid
from pydantic import BaseModel, field_validator
from domain.schema.user import UserBase

class UserDto(UserBase):
    id: uuid.UUID
    username: str
    created_at_utc: str
    
    # Field validators let you transform the data before it is validated in order to map schema to model fields
    @field_validator("id", mode="before")
    def validate_id(cls, v):
        return str(v)
    
    @field_validator("created_at_utc", mode="before")
    def validate_created_at_utc(cls, v):
        return str(v)
    
class UserOnboardingStatusDto(BaseModel):
    is_verified: bool
    is_first_course_created: bool
    recently_verified: bool