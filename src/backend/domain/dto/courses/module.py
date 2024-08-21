from typing import Optional
from domain.dto.courses.quiz import QuizDto
from domain.dto.courses.lesson import LessonDto
from domain.schema.courses.module import ModuleBase

class ModuleDto(ModuleBase):
    lessons: list[LessonDto]
    quiz: Optional[QuizDto] = None