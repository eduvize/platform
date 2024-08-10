from pydantic import field_validator
from typing import Optional
from domain.schema.profile.student import UserProfileStudentBase, UserProfileSchoolBase, UserProfileSchoolSkillBase

class UserProfileSchoolDto(UserProfileSchoolBase):
    school_name: str
    focus: Optional[str] = None
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