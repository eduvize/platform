from typing import Optional
import uuid
from pydantic import BaseModel

class CourseProgressionDto(BaseModel):
    is_course_complete: bool
    lesson_id: Optional[uuid.UUID]
    section_index: Optional[int]