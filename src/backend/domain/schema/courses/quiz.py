from enum import Enum
from sqlmodel import SQLModel

class QuizType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"

class QuizBase(SQLModel):
    title: str
    description: str
    quiz_type: QuizType