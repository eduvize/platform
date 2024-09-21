from pydantic import BaseModel

class TempCreateImageDto(BaseModel):
    base_image: str
    description: str