from typing import Optional
from pydantic import BaseModel

class Tool(BaseModel):
    name: str
    is_public: bool
    data: Optional[str] = None

class CompletionChunk(BaseModel):
    message_id: str
    received_text: Optional[str] = None
    text: Optional[str] = None
    audio: Optional[str] = None
    tools: Optional[list[Tool]] = None