from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from domain.schema.profile.learning_capacities import UserProfileProfessionalBase, UserProfileStudentBase
        
class UserProfileStudent(UserProfileStudentBase):
    pass        
            
class UserProfileProfessional(UserProfileProfessionalBase):
    pass