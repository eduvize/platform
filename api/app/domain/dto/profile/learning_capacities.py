from typing import List, Optional
from pydantic import BaseModel
from . import HobbyProjectDto

class UserProfileHobby(BaseModel):
    projects: Optional[List[HobbyProjectDto]] = None
    
    class Config:
        from_attributes = True
        
class UserProfileStudent(BaseModel):
        
    class Config:
        from_attributes = True
            
class UserProfileProfessional(BaseModel):
            
    class Config:
        from_attributes = True