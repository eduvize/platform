import uuid
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
import domain.schema as schema

class LessonBase(SQLModel):
    title: str          = Field(nullable=False)
    description: str    = Field(nullable=False)
    
class Lesson(LessonBase, table=True):
    __tablename__ = "course_lessons"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    module_id: uuid.UUID                            = Field(default=None, foreign_key="course_modules.id")
    
    module: "schema.courses.module.Module"          = Relationship(back_populates="lessons")
    sections: list["schema.courses.section.Section"]      = Relationship(back_populates="lesson")