from datetime import datetime
from typing import Optional
import uuid
from domain.dto.courses.module import ModuleDto
from domain.schema.courses.course import CourseBase

class CourseDto(CourseBase):
    id: uuid.UUID
    title: str
    description: str
    cover_image_url: str
    current_lesson_id: uuid.UUID
    lesson_index: int
    completed_at_utc: Optional[datetime]
    modules: list[ModuleDto]
    
class CourseListingDto(CourseBase):
    id: uuid.UUID
    title: str
    description: str
    cover_image_url: str
    progress: int
    is_generating: bool
    generation_progress: int