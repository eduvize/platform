from pydantic import BaseModel


class InstructorProfile(BaseModel):
    name: str