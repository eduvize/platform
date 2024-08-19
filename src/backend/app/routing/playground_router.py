from fastapi import APIRouter, Depends
from app.services import PlaygroundService
from .middleware import user_id_extractor
from .contracts.playground_contracts import (
    PlaygroundCreationResponse
)

router = APIRouter(
    prefix="/playground",
)

@router.post("/")
async def create_playground_instance(
    user_id: str = Depends(user_id_extractor),
    playground_service: PlaygroundService = Depends(PlaygroundService)
):
    session_id, token = await playground_service.create_playground(user_id)
    
    return PlaygroundCreationResponse.model_construct(
        session_id=session_id,
        token=token
    )