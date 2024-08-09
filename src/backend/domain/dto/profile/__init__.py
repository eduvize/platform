import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import computed_field, field_validator
from domain.schema.user import UserProfileBase, UserProfileSkillBase, UserProfileDisciplineBase
from domain.dto.profile.hobby import UserProfileHobbyDto
from domain.dto.profile.learning_capacities import UserProfileStudentDto, UserProfileProfessionalDto
from domain.enums.user_enums import UserDiscipline, UserLearningCapacity, UserSkillType

class UserSkillDto(UserProfileSkillBase):
    id: Optional[str] = None
    skill_type: UserSkillType
    skill: str
    proficiency: Optional[int] = 0
    notes: Optional[str] = None
    
    @field_validator("id", mode="plain")
    def validate_id(cls, v: str) -> str:
        if isinstance(v, uuid.UUID):
            return str(v)

        return v
    
class UserProfileDisciplineDto(UserProfileDisciplineBase):
    discipline_type: UserDiscipline
    proficiency: Optional[int] = None
    
class UserProfileDto(UserProfileBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate: Optional[datetime] = None
    bio: Optional[str] = None
    github_username: Optional[str] = None
    avatar_url: Optional[str] = None
    
    learning_capacities: Optional[List[str]] = None
    
    disciplines: Optional[List[UserProfileDisciplineDto]] = None
    skills: Optional[List[UserSkillDto]] = None
    
    hobby: Optional[UserProfileHobbyDto] = None
    student: Optional[UserProfileStudentDto] = None
    professional: Optional[UserProfileProfessionalDto] = None
    
    @computed_field
    @property
    def selected_learning_capacities(self) -> List[UserLearningCapacity]:
        l: UserLearningCapacity = []
        if self.hobby:
            l.append(UserLearningCapacity.HOBBY)
        if self.student:
            l.append(UserLearningCapacity.STUDENT)
        if self.professional:
            l.append(UserLearningCapacity.PROFESSIONAL)
        return l