from typing import Optional
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.schema.playground import PlaygroundSession, PlaygroundEnvironment
from common.database import get_async_session
from domain.enums.playground_enums import EnvironmentType

class PlaygroundRepository:
    async def create_playground_session(self, environment_id: uuid.UUID, hostname_override: Optional[str]) -> uuid.UUID:
        async for session in get_async_session():
            playground = PlaygroundSession(
                environment_id=environment_id,
                instance_hostname=hostname_override
            )
            session.add(playground)
            await session.commit()
            await session.refresh(playground)
            
            return playground.id
        
    async def create_environment(
        self,
        user_id: uuid.UUID,
        docker_base_image: str,
        description: str
    ) -> uuid.UUID:
        async for session in get_async_session():
            environment = PlaygroundEnvironment(
                user_id=user_id,
                docker_base_image=docker_base_image,
                description=description,
            )
            
            session.add(environment)
            await session.commit()
            await session.refresh(environment)
            
            return environment.id
        
    async def get_environment(
        self,
        environment_id: uuid.UUID,
    ) -> Optional[PlaygroundEnvironment]:
        async for session in get_async_session():
            environment = await session.get(PlaygroundEnvironment, environment_id)
            return environment
        
    async def set_environment_image_tag_and_type(
        self,
        environment_id: uuid.UUID,
        image_tag: str,
        env_type: EnvironmentType,
        resource_id: uuid.UUID,
    ):
        async for session in get_async_session():
            environment = await session.get(PlaygroundEnvironment, environment_id)
            
            if environment is None:
                raise ValueError("Environment not found")
            
            environment.image_tag = image_tag
            environment.type = env_type
            environment.resource_id = resource_id
            await session.commit()
            
    async def remove_environment(self, environment_id: uuid.UUID):
        async for session in get_async_session():
            environment = await session.get(PlaygroundEnvironment, environment_id)
            
            if environment is None:
                raise ValueError("Environment not found")
            
            await session.delete(environment)
            await session.commit()