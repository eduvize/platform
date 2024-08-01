from typing import Optional
from pydantic import BaseModel

class UpdateProfilePayload(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    github_username: Optional[str] = None
    avatar_file_id: Optional[str] = None