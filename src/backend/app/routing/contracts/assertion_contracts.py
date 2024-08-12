from pydantic import BaseModel

class AssertionResult(BaseModel):
    assertion: bool
    reason: str