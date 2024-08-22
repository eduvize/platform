from typing import Optional
from domain.dto.courses.lesson import LessonDto
from domain.schema.courses.module import ModuleBase

class ModuleDto(ModuleBase):
    title: str
    description: str
    lessons: list[LessonDto]