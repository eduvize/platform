from typing import Optional
from pydantic import BaseModel


class GitHubUser(BaseModel):
    name: Optional[str] = None
    username: str
    email_address: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None