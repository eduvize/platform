from typing import Optional
from pydantic import BaseModel

class SendChatMessagePayload(BaseModel):
    message: Optional[str] = None
    audio: Optional[str] = None
    expect_audio_response: bool
    
class CreateSessionResponse(BaseModel):
    session_id: str