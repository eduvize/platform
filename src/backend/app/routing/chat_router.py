import uuid
from fastapi import APIRouter, Depends
from app.routing.middleware import token_validator, user_id_extractor
from app.services import ChatService

router = APIRouter(
    prefix="/chat",
    dependencies=[
        Depends(token_validator),
        Depends(user_id_extractor)
    ]
)
    
@router.get("/{session_id}/history")
async def get_chat_history(
    session_id: uuid.UUID,
    chat_service: ChatService = Depends(ChatService),
    user_id: str = Depends(user_id_extractor)
):
    messages = await chat_service.get_history(
        user_id=user_id, 
        session_id=session_id
    )
    return messages
