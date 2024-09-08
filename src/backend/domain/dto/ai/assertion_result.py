from pydantic import BaseModel

class AssertionResultDto(BaseModel):
    assertion: bool
    reason: str