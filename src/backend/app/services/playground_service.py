from typing import Optional, Tuple
from fastapi import Depends
from app.repositories import PlaygroundRepository

class PlaygroundService:
    playground_repo: PlaygroundRepository
    
    def __init__(
        self, 
        playground_repo: PlaygroundRepository = Depends(PlaygroundRepository)
    ):
        self.playground_repo = playground_repo
        
    async def create_playground(self) -> None:
        await self.playground_repo.create_playground_session("basic")
    
    async def create_reservation(self, instance_hostname: str) -> Optional[Tuple[str, str]]:
        free_session = await self.playground_repo.get_unreserved_session()
        
        if free_session is None:
            return None
        
        await self.playground_repo.set_session_hostname(free_session.id, instance_hostname)
        
        return str(free_session.id), free_session.type
    
    async def validate_reservation(self, instance_hostname: str) -> bool:
        session = await self.playground_repo.get_session_by_hostname(instance_hostname)
        
        if session is None:
            return False
        
        return True