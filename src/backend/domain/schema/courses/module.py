from typing import Optional
from sqlmodel import SQLModel
from .lesson import LessonBase
from .quiz import QuizBase

class ModuleBase(SQLModel):
    title: str
    description: str
    lessons: list[LessonBase]
    
    quiz: Optional[QuizBase]