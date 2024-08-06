from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
        
class UserProfileStudent(BaseModel):
        
    class Config:
        from_attributes = True
            
class UserProfileProfessional(BaseModel):
            
    class Config:
        from_attributes = True