from domain.dto.courses.module import ModuleDto
from domain.schema.courses.course import CourseBase

class CourseDto(CourseBase):
    title: str
    description: str
    modules: list[ModuleDto]