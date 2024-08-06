from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class HobbyReason(Enum):
    LEARN_NEW_TECHNOLOGY = "learn_new_technology"
    ENTERTAINING = "entertaining"
    MAKE_MONEY = "make_money"
    DIVERSIFY_SKILLS = "diversify_skills"
    CHALLENGING = "challenging"
    CREATIVE_OUTLET = "creative_outlet"

class HobbyProjectDto(BaseModel):
    project_name: str
    description: str
    purpose: Optional[str]
    
    class Config:
        from_attributes = True
        
class UserProfileHobby(BaseModel):
    reasons: Optional[List[HobbyReason]] = None
    projects: Optional[List[HobbyProjectDto]] = None
    
    class Config:
        from_attributes = True