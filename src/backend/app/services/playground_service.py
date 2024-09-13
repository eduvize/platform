from typing import Optional, Tuple
import uuid
from fastapi import Depends
from config import get_playground_token_secret, get_playground_hostname_override, get_playground_session_override
from app.utilities.jwt import create_token
from common.messaging.producer import KafkaProducer
from common.messaging.topics import Topic
from domain.topics import BuildPlaygroundTopic
from app.repositories import PlaygroundRepository

class PlaygroundService:
    playground_repo: PlaygroundRepository
    
    def __init__(
        self, 
        playground_repo: PlaygroundRepository = Depends(PlaygroundRepository)
    ):
        self.playground_repo = playground_repo
        
    async def create_playground_session(self, user_id: str, environment_id: uuid.UUID) -> Tuple[str, str]:
        """
        Creates a new Playground session for a user. The playground orchestrator will pick up this new record
        and deploy a new instance after a short delay.

        Args:
            user_id (str): The ID of the user requesting the playground session

        Returns:
            Tuple[str, str]: The session ID and token for authorization
        """
        
        environment = self.playground_repo.get_environment(environment_id)
        
        if environment is None:
            raise ValueError("Environment not found")
        
        session_override = get_playground_session_override()
        hostname_override = get_playground_hostname_override()
        session_id = await self.playground_repo.create_playground_session(
            environment_id=environment_id,
            hostname_override=hostname_override
        ) if session_override is None else session_override
        
        signing_key = get_playground_token_secret()
        token = create_token(
            data={
                "session_id": str(session_id),
                "environment_id": str(environment_id),
                "user_id": user_id
            }, 
            secret=signing_key,
            expiration_minutes=5
        )
        
        return str(session_id), token
    
    async def temp_create_playground_image(self, base_image: str, description: str):
        kafka_producer = KafkaProducer()
        
        kafka_producer.produce_message(
            topic=Topic.BUILD_PLAYGROUND,
            message=BuildPlaygroundTopic(
                base_image=base_image,
                description=description
            )
        )