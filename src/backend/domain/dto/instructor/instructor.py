from domain.schema.instructor import InstructorBase


class InstructorDto(InstructorBase):
    name: str
    avatar_url: str
    is_approved: bool