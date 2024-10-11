import uuid
from pydantic import BaseModel

class InstructorDto(BaseModel):
    id: uuid.UUID
    name: str
    alias: str
