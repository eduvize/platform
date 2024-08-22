
from domain.schema.courses import SectionBase

class SectionDto(SectionBase):
    title: str
    description: str
    content: str