from pydantic import BaseModel

class SendChatMessagePayload(BaseModel):
    message: str
    
class CreateSessionResponse(BaseModel):
    session_id: str