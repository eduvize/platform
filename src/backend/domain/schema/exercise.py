import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Exercise(SQLModel, table=True):
    __tablename__ = "exercises"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    lesson_id: uuid.UUID                    = Field(default=None, foreign_key="lessons.id")
    user_id: uuid.UUID                      = Field(default=None, foreign_key="users.id")
    instructions: str                       = Field(nullable=False)
    expectations: str                       = Field(nullable=False)
    
    submissions: list["ExerciseSubmission"] = Relationship(back_populates="exercise")

class ExerciseSubmission(SQLModel, table=True):
    __tablename__ = "exercise_submissions"
    
    id: uuid.UUID                   = Field(default_factory=uuid.uuid4, primary_key=True)
    exercise_id: uuid.UUID          = Field(default=None, foreign_key="exercises.id")
    content: str                    = Field(nullable=False)
    created_at_utc: datetime        = Field(nullable=False, default_factory=datetime.utcnow)
    
    exercise: "Exercise"            = Relationship(back_populates="submissions")