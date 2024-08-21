from domain.dto.courses.module import ModuleDto
from domain.schema.courses.course import CourseBase

class CourseDto(CourseBase):
    modules: list[ModuleDto]