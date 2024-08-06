from app.common.database import Context
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid

class Exercise(Context):
    __tablename__ = "exercises"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id                   = Column(PG_UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    user_id                     = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    instructions                = Column(Text, nullable=False)
    expectations                = Column(Text, nullable=False)
    
    lesson                      = relationship("Lesson", back_populates="exercises", uselist=False)
    submissions                 = relationship("ExerciseSubmission", back_populates="exercise")
    user                        = relationship("User", uselist=False)
    
class ExerciseSubmission(Context):
    __tablename__ = "exercise_submissions"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exercise_id                 = Column(PG_UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False)
    content                     = Column(Text, nullable=False)
    created_at_utc              = Column(TIMESTAMP, nullable=False, default='now()')
    
    exercise                    = relationship("Exercise", back_populates="submissions", uselist=False)