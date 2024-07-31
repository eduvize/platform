from typing import Optional
from pydantic import BaseModel, field_validator

class UserProfileDto(BaseModel):
    first_name: str
    last_name: str
    bio: str
    github_username: Optional[str]
    avatar_url: Optional[str]
    
    # The config class allows you to specify how the model should be created
    class Config:
        from_attributes = True # This is used to create the model from a schema object

class UserDto(BaseModel):
    id: str
    username: str
    profile: UserProfileDto
    created_at_utc: str
    
    class Config:
        from_attributes = True
    
    # Field validators let you transform the data before it is validated in order to map schema to model fields
    @field_validator("id", mode="before")
    def validate_id(cls, v):
        return str(v)
    
    @field_validator("created_at_utc", mode="before")
    def validate_created_at_utc(cls, v):
        return str(v)