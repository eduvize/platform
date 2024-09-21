from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import SQLModel, Field, Relationship, ForeignKey

class PlaygroundEnvironmentBase(SQLModel):
    image_tag: Optional[str]    = Field(nullable=True)
    docker_base_image: str      = Field(nullable=False)
    description: str            = Field(nullable=False)

class PlaygroundEnvironment(PlaygroundEnvironmentBase, table=True):
    __tablename__ = "playground_environments"
    
    id: uuid.UUID               = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID          = Field(default=None, foreign_key="users.id")
    created_at_utc: datetime    = Field(default_factory=datetime.utcnow)
    last_used_at_utc: datetime  = Field(default=None, nullable=True)