from pydantic import BaseModel


class InstructorDto(BaseModel):
    avatar_url: str