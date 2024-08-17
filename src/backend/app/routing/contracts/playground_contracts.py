from pydantic import BaseModel

class PlaygroundHostnamePayload(BaseModel):
    hostname: str
    
class PlaygroundSessionResponse(BaseModel):
    session_id: str
    session_type: str
    
class PlaygroundFinalizerPayload(BaseModel):
    hostname: str