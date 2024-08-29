import uuid
from domain.dto.courses.module import ModuleDto
from domain.schema.courses.course import CourseBase

class CourseDto(CourseBase):
    title: str
    description: str
    cover_image_url: str
    modules: list[ModuleDto]
    
class CourseListingDto(CourseBase):
    id: uuid.UUID
    title: str
    description: str
    cover_image_url: str
    is_generating: bool
    generation_progress: int