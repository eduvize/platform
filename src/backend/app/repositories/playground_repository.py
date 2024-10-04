from typing import Optional
import uuid
from sqlmodel import Session, select
from domain.schema.playground import PlaygroundSession, PlaygroundEnvironment
from common.database import engine
from domain.enums.playground_enums import EnvironmentType

class PlaygroundRepository:
    async def create_playground_session(self, environment_id: uuid.UUID, hostname_override: Optional[str]) -> uuid.UUID:
        with Session(engine) as session:
            playground = PlaygroundSession(
                environment_id=environment_id,
                instance_hostname=hostname_override
            )
            session.add(playground)
            session.commit()
            session.refresh(playground)
            
            return playground.id
        
    def create_environment(
        self,
        user_id: uuid.UUID,
        docker_base_image: str,
        description: str
    ) -> uuid.UUID:
        with Session(engine) as session:
            environment = PlaygroundEnvironment(
                user_id=user_id,
                docker_base_image=docker_base_image,
                description=description,
            )
            
            session.add(environment)
            session.commit()
            session.refresh(environment)
            
            return environment.id
        
    def get_environment(
        self,
        environment_id: uuid.UUID,
    ) -> Optional[PlaygroundEnvironment]:
        with Session(engine) as session:
            environment = session.get(PlaygroundEnvironment, environment_id)
            return environment
        
    def set_environment_image_tag_and_type(
        self,
        environment_id: uuid.UUID,
        image_tag: str,
        env_type: EnvironmentType,
        resource_id: uuid.UUID,
    ):
        with Session(engine) as session:
            environment = session.get(PlaygroundEnvironment, environment_id)
            
            if environment is None:
                raise ValueError("Environment not found")
            
            environment.image_tag = image_tag
            environment.type = env_type
            environment.resource_id = resource_id
            session.commit()
            
    def remove_environment(self, environment_id: uuid.UUID):
        with Session(engine) as session:
            environment = session.get(PlaygroundEnvironment, environment_id)
            
            if environment is None:
                raise ValueError("Environment not found")
            
            session.delete(environment)
            session.commit()