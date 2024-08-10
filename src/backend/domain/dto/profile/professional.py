from pydantic import field_validator
from domain.schema.profile.professional import (
    UserProfileEmploymentBase, 
    UserProfileEmploymentSkillBase, 
    UserProfileProfessionalBase
)

class UserProfileEmploymentDto(UserProfileEmploymentBase):
    company_name: str
    position: str
    description: str
    is_current: bool
    skills: list[str] = []
    
    @field_validator("skills", mode="plain")
    def validate_skills(cls, v: list[str]) -> list[str]:
        values = []
        
        for skill in v:
            if isinstance(skill, UserProfileEmploymentSkillBase):
                values.append(skill.skill_id)
            else:
                values.append(skill)
                
        return values

class UserProfileProfessionalDto(UserProfileProfessionalBase):
    employers: list[UserProfileEmploymentDto] = []