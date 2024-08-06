from typing import Optional
from pydantic import BaseModel

class HobbyProjectDto(BaseModel):
    name: str
    description: str
    purpose: Optional[str]
    
    class Config:
        from_attributes = True