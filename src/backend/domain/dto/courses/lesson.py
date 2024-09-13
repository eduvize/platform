import uuid
from domain.schema.courses.lesson import LessonBase
from .section import SectionDto
from .exercise import ExerciseDto

class LessonDto(LessonBase):
    id: uuid.UUID
    title: str
    description: str
    order: int
    sections: list[SectionDto]
    exercises: list[ExerciseDto]