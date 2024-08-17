from pydantic import BaseModel

class PlaygroundSessionResponse(BaseModel):
    session_id: str
    session_type: str