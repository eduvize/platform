from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from . import HobbyProjectDto

class HobbyReason(Enum):
    LEARN_NEW_TECHNOLOGY = "learn_new_technology"
    ENTERTAINING = "entertaining"
    MAKE_MONEY = "make_money"
    DIVERSIFY_SKILLS = "diversify_skills"
    CHALLENGING = "challenging"
    CREATIVE_OUTLET = "creative_outlet"

class UserProfileHobby(BaseModel):
    reasons: Optional[List[HobbyReason]] = None
    projects: Optional[List[HobbyProjectDto]] = None
    
    class Config:
        from_attributes = True
        
class UserProfileStudent(BaseModel):
        
    class Config:
        from_attributes = True
            
class UserProfileProfessional(BaseModel):
            
    class Config:
        from_attributes = True