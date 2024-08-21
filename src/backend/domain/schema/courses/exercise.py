import uuid
from sqlmodel import Field, Relationship, SQLModel
import domain.schema as schema

class ExerciseBase(SQLModel):
    description: str
    
class Exercise(ExerciseBase, table=True):
    __tablename__ = "exercises"
    
    id: uuid.UUID                       = Field(default=None, primary_key=True)
    course_id: uuid.UUID                = Field(default=None, foreign_key="courses.id")
    
    lesson: "schema.courses.Lesson"     = Relationship(back_populates="exercise")