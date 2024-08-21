import uuid
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import domain.schema as schema

class ModuleBase(SQLModel):
    title: str
    description: str
    
class Module(ModuleBase, table=True):
    __tablename__ = "modules"
    
    id: uuid.UUID                               = Field(default=None, primary_key=True)
    course_id: uuid.UUID                        = Field(default=None, foreign_key="courses.id")
    
    course: "schema.courses.course.Course"              = Relationship(back_populates="modules")
    lessons: list["schema.courses.lesson.Lesson"]       = Relationship(back_populates="module")
    quiz: Optional["schema.courses.quiz.Quiz"]          = Relationship(back_populates="module")