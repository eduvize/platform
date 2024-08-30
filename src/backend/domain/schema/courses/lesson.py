import uuid
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
import domain.schema as schema
from domain.schema.courses.section import Section

class LessonBase(SQLModel):
    title: str          = Field(nullable=False)
    description: str    = Field(nullable=False)
    order: int          = Field(nullable=False)
    
class Lesson(LessonBase, table=True):
    __tablename__ = "course_lessons"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    module_id: uuid.UUID                    = Field(default=None, foreign_key="course_modules.id")
    
    module: "schema.courses.module.Module"  = Relationship(back_populates="lessons")
    sections: List[Section]                 = Relationship(back_populates="lesson")