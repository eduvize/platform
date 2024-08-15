import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from domain.schema.user import User

class CurriculumBase(SQLModel):
    title: str                                  = Field(nullable=False)
    description: str                            = Field(nullable=False)
    view_count: int                             = Field(nullable=False, default=0)
    enrollment_count: int                       = Field(nullable=False, default=0)
    created_at_utc: datetime                    = Field(nullable=False, default_factory=datetime.utcnow)

class Curriculum(CurriculumBase, table=True):
    __tablename__ = "curriculums"
    
    id: uuid.UUID                               = Field(default_factory=uuid.uuid4, primary_key=True)
    reviews: list["CurriculumReview"]           = Relationship(back_populates="curriculum")
    enrollments: list["CurriculumEnrollment"]   = Relationship(back_populates="curriculum")

class CurriculumReviewBase(SQLModel):
    curriculum_id: uuid.UUID            = Field(default=None, foreign_key="curriculums.id")
    user_id: uuid.UUID                  = Field(default=None, foreign_key="users.id")
    rating: float                       = Field(nullable=False)
    review: str                         = Field(nullable=False)
    created_at_utc: datetime            = Field(nullable=False, default_factory=datetime.utcnow)
    
class CurriculumReview(CurriculumReviewBase, table=True):
    __tablename__ = "curriculum_reviews"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    curriculum: Curriculum              = Relationship(back_populates="reviews")
    user: User                          = Relationship(back_populates="curriculum_reviews")

class CurriculumEnrollmentBase(SQLModel):
    curriculum_id: uuid.UUID            = Field(default=None, foreign_key="curriculums.id")
    user_id: uuid.UUID                  = Field(default=None, foreign_key="users.id")
    created_at_utc: datetime            = Field(nullable=False, default_factory=datetime.utcnow)
    
class CurriculumEnrollment(CurriculumEnrollmentBase, table=True):
    __tablename__ = "curriculum_enrollments"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    curriculum: Curriculum              = Relationship(back_populates="enrollments")
    user: User                          = Relationship(back_populates="curriculum_enrollments")