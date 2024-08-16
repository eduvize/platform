import uuid
from fastapi import Depends
from app.repositories import PlaygroundRepository

class PlaygroundService:
    playground_repo: PlaygroundRepository
    
    def __init__(
        self, 
        playground_repo: PlaygroundRepository = Depends(PlaygroundRepository)
    ):
        self.playground_repo = playground_repo
        
    def create_playground(self) -> uuid.UUID:
        id = self.playground_repo.create_playground_session("basic")
        
        return id