from typing import Literal
import uuid
from pydantic import BaseModel

class BuildPlaygroundTopic(BaseModel):
    purpose: Literal["exercise"]
    environment_id: uuid.UUID
    resource_id: uuid.UUID
    base_image: str
    description: str
    
class EnvironmentCreatedTopic(BaseModel):
    purpose: Literal["exercise"]
    environment_id: uuid.UUID
    resource_id: uuid.UUID
    image_tag: str
    
class EnvironmentBuildFailedTopic(BaseModel):
    purpose: Literal["exercise"]
    environment_id: uuid.UUID