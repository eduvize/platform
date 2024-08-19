from pydantic import BaseModel

class PlaygroundCreationResponse(BaseModel):
    session_id: str
    token: str