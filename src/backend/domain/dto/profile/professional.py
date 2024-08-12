from datetime import datetime, date
from typing import Optional, Union
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
    start_date: Optional[date] = None
    end_date: Optional[date] = None
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
    
    @classmethod
    @field_validator("start_date", "end_date", mode="plain")
    def validate_dates(cls, v: Optional[Union[date, str]]) -> Optional[date]:
        if v:
            if isinstance(v, date):
                return v
            elif isinstance(v, str):
                return datetime.strptime(v, "%Y-%m-%d").date()
        else:
            return None

class UserProfileProfessionalDto(UserProfileProfessionalBase):
    employers: list[UserProfileEmploymentDto] = []