import uuid
from ..dto.courses.exercise_plan import ExercisePlan
from typing import Literal, Optional
from pydantic import BaseModel

class BuildPlaygroundTopic(BaseModel):
    purpose: Literal["exercise"]
    environment_id: uuid.UUID
    resource_id: uuid.UUID
    data: ExercisePlan
    
    
class EnvironmentCreatedTopic(BaseModel):
    purpose: Literal["exercise"]
    environment_id: uuid.UUID
    resource_id: uuid.UUID
    image_tag: str
    
class EnvironmentBuildFailedTopic(BaseModel):
    purpose: Literal["exercise"]
    environment_id: uuid.UUID
    error: Optional[str] = None