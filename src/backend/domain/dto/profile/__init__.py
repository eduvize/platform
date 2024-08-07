from typing import List, Optional
from pydantic import BaseModel, computed_field
from domain.schema.user import UserProfileBase, UserProfileSkillBase
from domain.dto.profile.hobby import UserProfileHobbyDto
from domain.dto.profile.disciplines import UserProfileFrontend, UserProfileBackend, UserProfileDatabase, UserProfileDevops
from domain.dto.profile.learning_capacities import UserProfileStudent, UserProfileProfessional
from domain.enums.user_enums import UserDiscipline, UserLearningCapacity, UserSkillType

class UserSkillDto(UserProfileSkillBase):
    skill_type: UserSkillType
    skill: str
    proficiency: Optional[int]
    notes: Optional[str]
    
class UserProfileDto(UserProfileBase):
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    github_username: Optional[str]
    avatar_url: Optional[str]
    
    skills: Optional[List[UserSkillDto]] = None
    
    hobby: Optional[UserProfileHobbyDto] = None
    student: Optional[UserProfileStudent] = None
    professional: Optional[UserProfileProfessional] = None
    
    frontend: Optional[UserProfileFrontend] = None
    backend: Optional[UserProfileBackend] = None
    database: Optional[UserProfileDatabase] = None
    devops: Optional[UserProfileDevops] = None
    
    @computed_field
    @property
    def learning_capacities(self) -> List[UserLearningCapacity]:
        l: UserLearningCapacity = []
        if self.hobby:
            l.append(UserLearningCapacity.HOBBY)
        if self.student:
            l.append(UserLearningCapacity.STUDENT)
        if self.professional:
            l.append(UserLearningCapacity.PROFESSIONAL)
        return l
    
    @computed_field
    @property
    def disciplines(self) -> List[UserDiscipline]:
        l: UserDiscipline = []
        if self.frontend:
            l.append(UserDiscipline.FRONTEND)
        if self.backend:
            l.append(UserDiscipline.BACKEND)
        if self.database:
            l.append(UserDiscipline.DATABASE)
        if self.devops:
            l.append(UserDiscipline.DEVOPS)
            
        return l