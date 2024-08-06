from pydantic import BaseModel

class UserProfileFrontend(BaseModel):
        
    class Config:
        from_attributes = True

class UserProfileBackend(BaseModel):
    
    class Config:
        from_attributes = True

class UserProfileDatabase(BaseModel):
        
    class Config:
        from_attributes = True

class UserProfileDevops(BaseModel):
        
    class Config:
        from_attributes = True