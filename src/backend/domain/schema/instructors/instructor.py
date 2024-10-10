import uuid
from sqlmodel import Field, SQLModel

class InstructorBase(SQLModel):
    name: str                   = Field(nullable=False)
    alias: str                  = Field(nullable=False)
    image_url: str              = Field(nullable=False) 

class Instructor(InstructorBase, table=True):
    __tablename__ = "instructors"
    
    id: uuid.UUID               = Field(default_factory=uuid.uuid4, primary_key=True)
    personality_prompt: str     = Field(nullable=False)