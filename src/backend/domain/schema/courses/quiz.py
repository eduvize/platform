import uuid
from sqlmodel import Field, Relationship, SQLModel
import domain.schema as schema
from datetime import datetime
from enum import Enum

class QuizType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"

class QuizBase(SQLModel):
    title: str
    description: str
    quiz_type: QuizType
    
class Quiz(QuizBase, table=True):
    __tablename__ = "quizzes"
    
    id: uuid.UUID                                   = Field(default_factory=uuid.uuid4, primary_key=True)
    course_id: uuid.UUID                            = Field(default=None, foreign_key="courses.id")
    created_at_utc: datetime                        = Field(default_factory=datetime.utcnow, nullable=False)
    
    module: "schema.courses.Module"                 = Relationship(back_populates="quiz")