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
        
    async def get_unreserved_session(self) -> Optional[PlaygroundSession]:
        with Session(engine) as session:
            query = select(PlaygroundSession).where(PlaygroundSession.instance_hostname == None)
            return session.exec(query).first()
        
    async def get_session_by_hostname(self, hostname: str) -> Optional[PlaygroundSession]:
        with Session(engine) as session:
            query = select(PlaygroundSession).where(PlaygroundSession.instance_hostname == hostname)
            return session.exec(query).first()
        
    async def set_session_hostname(self, session_id: uuid.UUID, hostname: str) -> None:
        with Session(engine) as session:
            query = select(PlaygroundSession).where(PlaygroundSession.id == session_id)
            playground = session.exec(query).first()
            playground.instance_hostname = hostname
            session.commit()