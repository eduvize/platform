import uuid
from fastapi import APIRouter, Depends
from app.services import PlaygroundService
from .middleware import user_id_extractor
from .contracts.playground_contracts import (
    PlaygroundCreationResponse
)
from domain.dto.playground.temp_create_image import TempCreateImageDto

router = APIRouter(
    prefix="/playground"
)

@router.get("/{environment_id}", dependencies=[Depends(user_id_extractor)])
async def create_playground_instance(
    environment_id: uuid.UUID,
    user_id: str = Depends(user_id_extractor),
    playground_service: PlaygroundService = Depends(PlaygroundService)
):
    session_id, token = await playground_service.create_playground_session(user_id, environment_id)
    
    return PlaygroundCreationResponse.model_construct(
        session_id=session_id,
        token=token
    )
    
@router.post("/setup", dependencies=[Depends(user_id_extractor)])
async def temp_create_playground(
    payload: TempCreateImageDto,
    user_id: str = Depends(user_id_extractor),
    playground_service: PlaygroundService = Depends(PlaygroundService)
):
    await playground_service.temp_create_playground_image(
        base_image=payload.base_image,
        description=payload.description
    )