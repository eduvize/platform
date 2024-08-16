from fastapi import APIRouter, Depends
from app.services import PlaygroundService

router = APIRouter(
    prefix="/playground",
)

@router.post("/")
async def verify_user(
    playground_service: PlaygroundService = Depends(PlaygroundService)
):
    playground_service.create_playground()