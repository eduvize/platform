from pydantic import BaseModel, field_validator, computed_field
from domain.dto.profile import UserProfileDto

class UserDto(BaseModel):
    id: str
    username: str
    profile: UserProfileDto
    created_at_utc: str
    
    @computed_field
    @property
    def display_name(self) -> str:
        return (
            f"{self.profile.first_name} {self.profile.last_name}" 
            if self.profile.first_name and self.profile.last_name 
            else self.username
        )
    
    class Config:
        from_attributes = True
    
    # Field validators let you transform the data before it is validated in order to map schema to model fields
    @field_validator("id", mode="before")
    def validate_id(cls, v):
        return str(v)
    
    @field_validator("created_at_utc", mode="before")
    def validate_created_at_utc(cls, v):
        return str(v)
    
class UserOnboardingStatusDto(BaseModel):
    is_verified: bool
    is_profile_complete: bool
    recently_verified: bool
    
    class Config:
        from_attributes = True