from typing import List
import uuid
from sqlmodel import SQLModel, Field, Relationship
import domain.schema as schema
from domain.schema.courses.lesson import Lesson

class ModuleBase(SQLModel):
    title: str          = Field(nullable=False)
    description: str    = Field(nullable=False)
    order: int          = Field(nullable=False)
    
class Module(ModuleBase, table=True):
    __tablename__ = "course_modules"
    
    id: uuid.UUID                               = Field(default_factory=uuid.uuid4, primary_key=True)
    course_id: uuid.UUID                        = Field(default=None, foreign_key="courses.id")
    
    course: "schema.courses.course.Course"      = Relationship(back_populates="modules")
    lessons: List[Lesson]                       = Relationship(back_populates="module")