import uuid
from domain.schema.courses.lesson import LessonBase
from .section import SectionDto

class LessonDto(LessonBase):
    id: uuid.UUID
    title: str
    description: str
    sections: list[SectionDto]