import uuid
from app.common.database import Context
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

class Lesson(Context):
    __tablename__ = "lessons"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    curriculum_id               = Column(PG_UUID(as_uuid=True), ForeignKey("curriculums.id"), nullable=False)
    title                       = Column(Text, nullable=False)
    description                 = Column(Text, nullable=False)
    curriculum_index            = Column(Integer, nullable=False)
    
    curriculum                  = relationship("Curriculum", back_populates="lessons", uselist=False)
    exercises                   = relationship("Exercise", back_populates="lesson")