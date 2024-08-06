from typing import List, Optional
from pydantic import BaseModel, computed_field
from .disciplines import UserProfileFrontend, UserProfileBackend, UserProfileDatabase, UserProfileDevops
from .learning_capacities import UserProfileHobby, UserProfileStudent, UserProfileProfessional
from .hobby import HobbyProjectDto
from ....domain.enums.user_enums import UserDiscipline, UserLearningCapacity, UserSkillType

class UserSkill(BaseModel):
    skill_type: UserSkillType
    skill: str
    proficiency: Optional[int]
    notes: Optional[str]
    
    class Config:
        from_attributes = True

class UserProfileDto(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    github_username: Optional[str]
    avatar_url: Optional[str]
    
    skills: Optional[List[UserSkill]] = None
    
    hobby: Optional[UserProfileHobby] = None
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
    
    class Config:
        from_attributes = True