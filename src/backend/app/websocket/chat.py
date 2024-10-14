import json
import logging
from uuid import UUID
from fastapi import Depends
from socketio import AsyncNamespace
from app.services.chat_service import ChatService
from app.services.user_service import UserService
from app.utilities.jwt import decode_token, InvalidJWTToken
from domain.enums.chat_enums import PromptType
from config import get_token_secret
from .dependency_resolver import inject_dependencies
from .util import get_token_from_environ

class ChatNamespace(AsyncNamespace):
    """
    Namespace for chat-related events.
    All methods starting with 'on_' are automatically registered as event handlers.
    """

    def __init__(self, namespace):
        super().__init__(namespace)

    @inject_dependencies()
    async def on_connect(self, sid: str, environ: dict, user_service: UserService = Depends(), chat_service: ChatService = Depends()):
        token = get_token_from_environ(environ)
        logging.info(token)
        
        try:
            decoded = decode_token(token=token, secret=get_token_secret())
            user_id = decoded["id"]
            
            session = await self.get_session(sid)
            session["user_id"] = user_id
            
            user = await user_service.get_user("id", user_id)
            
            if not user.default_instructor_id:
                raise ValueError("User does not have a default instructor")
            
            session["instructor_id"] = user.default_instructor_id
            
            chat_session = await chat_service.create_session(
                user_id=user_id
            )
            
            session["chat_session_id"] = chat_session.id
            
            logging.info(f"User {user_id} connected to chat")
            
        except InvalidJWTToken:
            logging.info(f"Connection from {sid} failed due to invalid token")
            return False
        
        return True

    async def on_disconnect(self, sid: str):
        logging.info(f"User disconnected from chat: {sid}")

    @inject_dependencies()
    async def on_send_message(self, sid: str, data: dict, chat_service: ChatService = Depends()):
        session = await self.get_session(sid)
        user_id = session.get("user_id")
        prompt_type = session.get("prompt_type")
        use_voice = session.get("use_voice", False)
        instructor_id = session.get("instructor_id")
        chat_session_id = session.get("chat_session_id")
        
        if not prompt_type:
            raise ValueError("Prompt type not found")
        
        if not chat_session_id:
            raise ValueError("Chat session ID not found")
        
        async for chunk in chat_service.get_response(
            user_id=user_id,
            session_id=chat_session_id,
            instructor_id=instructor_id,
            prompt_type=prompt_type,
            message=data.get("message"),
            audio=data.get("audio"),
            expect_audio_response=use_voice
        ):
            await self.emit("message_update", json.loads(chunk.model_dump_json()), to=sid)
        
        await self.emit("message_complete", to=sid)
        
    async def on_set_instructor(self, sid: str, data: dict):
        instructor_id = data.get("instructor_id")
        session = await self.get_session(sid)
        session["instructor_id"] = instructor_id
        
    @inject_dependencies()
    async def on_set_prompt(self, sid: str, data: dict, chat_service: ChatService = Depends()):
        prompt_type = data.get("prompt_type")
        session = await self.get_session(sid)
        session["prompt_type"] = PromptType(prompt_type)
        
    async def on_use_voice(self, sid: str, data: dict):
        enabled = data.get("enabled", False)
        session = await self.get_session(sid)
        session["use_voice"] = enabled
