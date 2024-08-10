from enum import Enum
from typing import Annotated, Any, Optional
from pydantic import (
    BeforeValidator, 
    PlainValidator, 
    ValidationInfo, 
    ValidatorFunctionWrapHandler, 
    WrapValidator, 
    field_validator
)
from domain.schema.profile.hobby import (
    UserProfileHobbyBase, 
    UserProfileHobbyProjectBase, 
    UserProfileHobbyReasonBase, 
    UserProfileHobbySkillBase
)

class HobbyReason(Enum):
    LEARN_NEW_TECHNOLOGY = "learn_new_technology"
    ENTERTAINING = "entertaining"
    MAKE_MONEY = "make_money"
    DIVERSIFY_SKILLS = "diversify_skills"
    CHALLENGING = "challenging"
    CREATIVE_OUTLET = "creative_outlet"

class HobbyProjectDto(UserProfileHobbyProjectBase):
    project_name: str
    description: str
    purpose: Optional[str] = None
        
class UserProfileHobbyDto(UserProfileHobbyBase):
    reasons: list[HobbyReason] = []
    projects: list[HobbyProjectDto] = []
    skills: list[str] = []
    
    @field_validator("skills", mode="plain")
    def validate_skills(cls, v: list[str]) -> list[str]:
        values = []
        
        for skill in v:
            if isinstance(skill, UserProfileHobbySkillBase):
                values.append(skill.skill_id)
            else:
                values.append(skill)
                
        return values
    
    @field_validator("reasons", mode="before")
    def validate_reasons(cls, v: list[HobbyReason]) -> list[HobbyReason]:
        values = []
        
        for reason in v:
            if isinstance(reason, UserProfileHobbyReasonBase):
                values.append(reason.reason)
            else:
                values.append(reason)
                
        return values