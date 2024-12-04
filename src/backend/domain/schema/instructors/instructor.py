import uuid
from sqlmodel import Field, SQLModel

class InstructorBase(SQLModel):
    name: str                   = Field(nullable=False)
    alias: str                  = Field(nullable=False)
    image_url: str              = Field(nullable=False) 
    sample_text: str            = Field(nullable=False)
    enthusiasm: int             = Field(nullable=False)
    structure: int              = Field(nullable=False)
    support: int                = Field(nullable=False)

class Instructor(InstructorBase, table=True):
    __tablename__ = "instructors"
    
    id: uuid.UUID               = Field(default_factory=uuid.uuid4, primary_key=True)
    personality_prompt: str     = Field(nullable=False)
    voice_id: str               = Field(nullable=False)