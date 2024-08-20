import asyncio
import json
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.routing.middleware import token_validator, user_id_extractor
from app.services import ChatService
from .contracts.chat_contracts import ChatSessionReference, SendChatMessage

router = APIRouter(
    prefix="/chat",
    dependencies=[
        Depends(token_validator),
        Depends(user_id_extractor)
    ]
)

@router.post("/")
async def send_message(
    payload: SendChatMessage,
    chat_service: ChatService = Depends(ChatService),
    user_id: str = Depends(user_id_extractor)
):
    # This function generates a stream of messages
    async def message_stream():
        async for message in chat_service.get_response(user_id, payload):
            yield f"{message.model_dump_json()}\n\n"
            await asyncio.sleep(0.01)

    response = StreamingResponse(message_stream(), media_type="text/event-stream")
    return response
    
@router.get("/history")
async def get_chat_history(
    chat_service: ChatService = Depends(ChatService),
    user_id: str = Depends(user_id_extractor)
):
    messages = await chat_service.get_history(user_id)
    return messages

@router.get("/curriculums/:curriculum_id/history")
async def get_course_chat_history(
    curriculum_id: uuid.UUID,
    chat_service: ChatService = Depends(ChatService),
    user_id: str = Depends(user_id_extractor)
):
    messages = await chat_service.get_history(user_id, ChatSessionReference(curriculum_id=curriculum_id))
    return messages

@router.get("/lessons/:lesson_id/history")
async def get_lesson_chat_history(
    lesson_id: uuid.UUID,
    chat_service: ChatService = Depends(ChatService),
    user_id: str = Depends(user_id_extractor)
):
    messages = await chat_service.get_history(user_id, ChatSessionReference(lesson_id=lesson_id))
    return messages

@router.get("/exercises/:exercise_id/history")
async def get_exercise_chat_history(
    exercise_id: uuid.UUID,
    chat_service: ChatService = Depends(ChatService),
    user_id: str = Depends(user_id_extractor)
):
    messages = await chat_service.get_history(user_id, ChatSessionReference(exercise_id=exercise_id))
    return messages