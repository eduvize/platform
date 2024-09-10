from typing import Tuple
from fastapi import Depends
from config import get_playground_token_secret, get_playground_session_id_override
from app.utilities.jwt import create_token
from app.repositories import PlaygroundRepository

class PlaygroundService:
    playground_repo: PlaygroundRepository
    
    def __init__(
        self, 
        playground_repo: PlaygroundRepository = Depends(PlaygroundRepository)
    ):
        self.playground_repo = playground_repo
        
    async def create_playground(self, user_id: str) -> Tuple[str, str]:
        """
        Creates a new Playground session for a user. The playground orchestrator will pick up this new record
        and deploy a new instance after a short delay.

        Args:
            user_id (str): The ID of the user requesting the playground session

        Returns:
            Tuple[str, str]: The session ID and token for authorization
        """
        session_override = get_playground_session_id_override()
        session_id = await self.playground_repo.create_playground_session("basic") if session_override is None else session_override
        
        signing_key = get_playground_token_secret()
        token = create_token(
            data={
                "session_id": str(session_id), 
                "user_id": user_id
            }, 
            secret=signing_key,
            expiration_minutes=5
        )
        
        return str(session_id), token