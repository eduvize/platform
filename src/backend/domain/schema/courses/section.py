import uuid
from sqlmodel import SQLModel, Field, Relationship
import domain.schema as schema

class SectionBase(SQLModel):
    title: str          = Field(nullable=False)
    description: str    = Field(nullable=False)
    content: str        = Field(nullable=False)
    order: int          = Field(nullable=False)
    
class Section(SectionBase, table=True):
    __tablename__ = "course_lesson_sections"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    lesson_id: uuid.UUID                    = Field(default=None, foreign_key="course_lessons.id")
    
    lesson: "schema.courses.lesson.Lesson"  = Relationship(back_populates="sections")