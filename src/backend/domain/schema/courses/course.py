import uuid
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
import domain.schema as schema

class CourseBase(SQLModel):
    title: str
    description: str
    
class Course(CourseBase, table=True):
    __tablename__ = "courses"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID                      = Field(default=None, foreign_key="users.id")
    created_at_utc: datetime                = Field(default_factory=datetime.utcnow, nullable=False)
    
    modules: list["schema.courses.Module"]  = Relationship(back_populates="course")
    
    user: "schema.user.User"                = Relationship(back_populates="courses")