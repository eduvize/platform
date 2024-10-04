from typing import List, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
import domain.schema as schema
from domain.schema.courses.module import Module

class CourseBase(SQLModel):
    title: str                              = Field(nullable=False)
    description: str                        = Field(nullable=False)
    cover_image_url: str                    = Field(nullable=False) 
    is_generating: bool                     = Field(default=True, nullable=False)
    generation_progress: int                = Field(default=0, nullable=False)
    current_lesson_id: Optional[uuid.UUID]  = Field(default=None, nullable=True)
    completed_at_utc: Optional[datetime]    = Field(default=None, nullable=True)
    
class Course(CourseBase, table=True):
    __tablename__ = "courses"
    
    id: uuid.UUID               = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID          = Field(default=None, foreign_key="users.id")
    created_at_utc: datetime    = Field(default_factory=datetime.utcnow, nullable=False)
    
    modules: List[Module]       = Relationship(back_populates="course")
    
    user: "schema.user.User"    = Relationship(back_populates="courses")