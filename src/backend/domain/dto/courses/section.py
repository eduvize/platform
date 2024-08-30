
from domain.schema.courses import SectionBase

class SectionDto(SectionBase):
    title: str
    description: str
    order: int
    content: str