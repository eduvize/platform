from typing import Optional
import uuid
from sqlmodel import Session, select
from domain.schema.playground.playground_session import PlaygroundSession
from common.database import engine

class PlaygroundRepository:
    async def create_playground_session(self, type: str) -> uuid.UUID:
        with Session(engine) as session:
            playground = PlaygroundSession(type=type)
            session.add(playground)
            session.commit()
            session.refresh(playground)
            
            return playground.id