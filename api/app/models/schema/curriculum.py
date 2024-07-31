import uuid

from sqlalchemy import TIMESTAMP, Column, Double, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from ...common.database import Context

class Curriculum(Context):
    __tablename__ = "curriculums"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title                       = Column(Text, nullable=False)
    description                 = Column(Text, nullable=False)
    view_count                  = Column(Integer, nullable=False, default=0)
    enrollment_count            = Column(Integer, nullable=False, default=0)
    created_at_utc              = Column(TIMESTAMP, nullable=False, default='now()')
    
    reviews                    = relationship("CurriculumReview", back_populates="curriculum")
    enrollments                = relationship("CurriculumEnrollment", back_populates="curriculum")
    lessons                    = relationship("Lesson", back_populates="curriculum")
    
class CurriculumReview(Context):
    __tablename__ = "curriculum_reviews"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    curriculum_id               = Column(PG_UUID(as_uuid=True), ForeignKey("curriculums.id"), nullable=False)
    user_id                     = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rating                      = Column(Double, nullable=False)
    review                      = Column(Text, nullable=False)
    created_at_utc              = Column(TIMESTAMP, nullable=False, default='now()')
    
    curriculum                  = relationship("Curriculum", back_populates="reviews", uselist=False)
    user                        = relationship("User", uselist=False)
    
class CurriculumEnrollment(Context):
    __tablename__ = "curriculum_enrollments"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    curriculum_id               = Column(PG_UUID(as_uuid=True), ForeignKey("curriculums.id"), nullable=False)
    user_id                     = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at_utc              = Column(TIMESTAMP, nullable=False, default='now()')
    
    curriculum                  = relationship("Curriculum", back_populates="enrollments", uselist=False)
    user                        = relationship("User", uselist=False)