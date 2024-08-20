from typing import Optional
from sqlmodel import SQLModel
from .exercise import ExerciseBase

class LessonBase(SQLModel):
    title: str
    description: str
    
    exercise: Optional[ExerciseBase]