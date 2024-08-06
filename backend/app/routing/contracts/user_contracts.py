from typing import List, Optional
from pydantic import BaseModel

class UpdateProfilePayload(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    github_username: Optional[str] = None
    avatar_file_id: Optional[str] = None
    learning_capacities: Optional[List[str]] = None
    disciplines: Optional[List[str]] = None