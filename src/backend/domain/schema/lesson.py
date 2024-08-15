import uuid
from sqlmodel import SQLModel, Field, Relationship

class LessonBase(SQLModel):
    curriculum_id: uuid.UUID        = Field(default=None, foreign_key="curriculums.id")
    title: str                      = Field(nullable=False)
    description: str                = Field(nullable=False)
    curriculum_index: int           = Field(nullable=False)

class Lesson(LessonBase, table=True):
    __tablename__ = "lessons"
    id: uuid.UUID                   = Field(default_factory=uuid.uuid4, primary_key=True)