from typing import Optional

from pydantic import field_validator
from domain.schema.courses.lesson import LessonBase
from .section import SectionDto

class LessonDto(LessonBase):
    title: str
    description: str
    sections: list[SectionDto]