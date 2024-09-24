import uuid
from pydantic import BaseModel

class InternalExerciseObjectiveDto(BaseModel):
    id: uuid.UUID
    objective: str
    test_plan: str
    is_completed: bool
    
class InternalExerciseDto(BaseModel):
    id: uuid.UUID
    title: str
    summary: str
    objectives: list[InternalExerciseObjectiveDto]