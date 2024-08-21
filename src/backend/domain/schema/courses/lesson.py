import uuid
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
import domain.schema as schema

class LessonBase(SQLModel):
    title: str
    description: str
    
class Lesson(LessonBase, table=True):
    __tablename__ = "lessons"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    module_id: uuid.UUID                            = Field(default=None, foreign_key="modules.id")
    
    module: "schema.courses.module.Module"                  = Relationship(back_populates="lessons")
    
    exercise: Optional["schema.courses.exercise.Exercise"]  = Relationship(back_populates="lesson")