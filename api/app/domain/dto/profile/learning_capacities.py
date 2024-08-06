from pydantic import BaseModel

class UserProfileHobby(BaseModel):
    
    class Config:
        from_attributes = True
        
class UserProfileStudent(BaseModel):
        
    class Config:
        from_attributes = True
            
class UserProfileProfessional(BaseModel):
            
    class Config:
        from_attributes = True