from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from domain.schema.profile.learning_capacities import UserProfileProfessionalBase, UserProfileStudentBase
        
class UserProfileStudentDto(UserProfileStudentBase):
    pass  
            
class UserProfileProfessionalDto(UserProfileProfessionalBase):
    pass