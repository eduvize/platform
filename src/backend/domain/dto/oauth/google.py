from typing import Optional
from pydantic import BaseModel


class GoogleUser(BaseModel):
    name: Optional[str] = None
    username: str
    email_address: str
    avatar_url: Optional[str] = None