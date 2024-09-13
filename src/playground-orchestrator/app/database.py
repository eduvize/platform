import os
import uuid
from typing import Optional
from datetime import datetime
from sqlmodel import Field, create_engine, Session, select
from sqlmodel import SQLModel, Relationship
from sqlalchemy.orm import joinedload

class PlaygroundEnvironment(SQLModel, table=True):
    __tablename__ = "playground_environments"
    
    id: uuid.UUID               = Field(default_factory=uuid.uuid4, primary_key=True)
    image_tag: Optional[str]    = Field(nullable=True)
    docker_base_image: str      = Field(nullable=False)
    description: str            = Field(nullable=False)
    user_id: uuid.UUID          = Field(default=None, foreign_key="users.id")
    created_at_utc: datetime    = Field(default_factory=datetime.utcnow)
    last_used_at_utc: datetime  = Field(default=None, nullable=True)
    
    sessions: list["PlaygroundSession"] = Relationship(back_populates="environment")

# Database model for the playground_sessions table
class PlaygroundSession(SQLModel, table=True):
    __tablename__ = "playground_sessions"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    environment_id: uuid.UUID           = Field(nullable=False, foreign_key="playground_environments.id")
    instance_hostname: Optional[str]    = Field(nullable=True)
    created_at_utc: datetime            = Field(default_factory=datetime.utcnow)
    
    environment: PlaygroundEnvironment = Relationship(back_populates="sessions")

def get_db_session():
    connection_string = os.getenv("POSTGRES_CONNECTION_STRING")
    engine = create_engine(connection_string)
    session = Session(engine)
    return session

def get_unreserved_sessions():
    session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.instance_hostname == None).options(joinedload(PlaygroundSession.environment))
    result = session.exec(statement).all()
    session.close()
    return result

def remove_session(session_id: uuid.UUID):
    session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.id == session_id)
    result = session.exec(statement).first()
    
    if result is not None:
        session.delete(result)
        session.commit()
        
    session.close()

def assign_session(session_id: uuid.UUID, instance_hostname: str):
    """
    Updates a session with the instance hostname of the pod it is assigned to

    Args:
        session_id (uuid.UUID): The session ID
        instance_hostname (str): The hostname of the pod
    """
    
    db_session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.id == session_id)
    result = db_session.exec(statement).one()
    result.instance_hostname = instance_hostname
    db_session.commit()
    db_session.close()

def unassign_session(session_id: uuid.UUID):
    session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.id == session_id)
    result = session.exec(statement).one()
    result.instance_hostname = None
    session.add(result)
    session.commit()
    session.close()

def get_reserved_sessions():
    session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.instance_hostname != None).options(joinedload(PlaygroundSession.environment))
    result = session.exec(statement).all()
    session.close()
    return result