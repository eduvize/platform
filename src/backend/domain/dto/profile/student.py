from datetime import datetime, date
from pydantic import field_validator
from typing import Optional, Union
from domain.schema.profile.student import UserProfileStudentBase, UserProfileSchoolBase, UserProfileSchoolSkillBase

class UserProfileSchoolDto(UserProfileSchoolBase):
    school_name: str
    focus: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    did_finish: bool
    is_current: bool
    skills: list[str] = []
    
    @field_validator("skills", mode="plain")
    def validate_skills(cls, v: list[str]) -> list[str]:
        values = []
        
        for skill in v:
            if isinstance(skill, UserProfileSchoolSkillBase):
                values.append(skill.skill_id)
            else:
                values.append(skill)
                
        return values

class UserProfileStudentDto(UserProfileStudentBase):
    schools: list[UserProfileSchoolDto] = []