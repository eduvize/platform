import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field

class PlaygroundSessionBase(SQLModel):
    id: uuid.UUID               = Field(default_factory=uuid.uuid4, primary_key=True)
    type: str                   = Field(nullable=False)
    is_reserved: bool           = Field(default=False)
    created_at_utc: datetime    = Field(default_factory=datetime.utcnow)
    
class PlaygroundSession(PlaygroundSessionBase, table=True):
    __tablename__ = "playground_sessions"