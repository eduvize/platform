import json
import logging
from typing import Optional
from uuid import UUID
from fastapi import Depends
from socketio import AsyncNamespace
from app.services import ChatService, UserService, UserOnboardingService, InstructorService
from app.utilities.jwt import decode_token, InvalidJWTToken
from domain.enums.chat_enums import PromptType
from config import get_token_secret, get_deepgram_api_key
from ..dependency_resolver import inject_dependencies
from ..util import get_token_from_environ
from deepgram import DeepgramClient, DeepgramClientOptions, LiveOptions, LiveTranscriptionEvents
from deepgram.clients import AsyncListenWebSocketClient, LiveResultResponse

class ChatNamespace(AsyncNamespace):
    """
    Namespace for chat-related events.
    All methods starting with 'on_' are automatically registered as event handlers.
    """
    
    def __init__(self, namespace):
        """
        Initialize the ChatNamespace.

        Args:
            namespace (str): The namespace for the chat events.
        """
        super().__init__(namespace)
        
        options = DeepgramClientOptions(options={"keepalive": "true"})
        self.deepgram_client = DeepgramClient(get_deepgram_api_key(), options)
        self.deepgram_connections: dict[str, AsyncListenWebSocketClient] = {}

    # Connection handling methods
    @inject_dependencies()
    async def on_connect(
        self, 
        sid: str, 
        environ: dict, 
        user_service: UserService = Depends(), 
        chat_service: ChatService = Depends(),
        user_onboarding_service: UserOnboardingService = Depends(),
        instructor_service: InstructorService = Depends()
    ):
        """
        Handle client connection.

        Args:
            sid (str): Session ID.
            environ (dict): Environment variables.
            user_service (UserService): User service dependency.
            chat_service (ChatService): Chat service dependency.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        token = get_token_from_environ(environ)
        logging.info(token)
        
        try:
            decoded = decode_token(token=token, secret=get_token_secret())
            user_id: Optional[str] = decoded.get("id", None)
            
            if not user_id:
                raise ValueError("User ID not found in token")
            
            session = await self.get_session(sid)
            session["user_id"] = user_id
            
            user = await user_service.get_user("id", user_id)
            onboarding_state = await user_onboarding_service.get_onboarding_status(user_id)
            
            if user.default_instructor_id:
                instructor = await instructor_service.get_instructor_by_id(user.default_instructor_id)
                session["instructor_id"] = user.default_instructor_id
            else:
                instructor = None
            
            # Lock the user into the onboarding session if they haven't created their first course yet
            if not onboarding_state.is_first_course_created:
                session["prompt_type"] = PromptType.ONBOARDING
                
                if user.onboarding_session_id and instructor:
                    chat_session = await chat_service.get_session(user.onboarding_session_id)
                    session["chat_session_id"] = user.onboarding_session_id
                    
                    await self.emit("continue_session", str(user.onboarding_session_id), to=sid)
                    await self.on_send_message(sid, {"message": f"Hello, {instructor.name}! I'm back from a break - where were we?", "hide_from_chat": True})
                else:
                    chat_session = await chat_service.create_session(user_id=user_id)
                    session["chat_session_id"] = chat_session.id

                    await user_service.set_onboarding_session_id(user_id, chat_session.id)
                    await self.emit("start_session", str(chat_session.id), to=sid)
            else:
                pass # All other cases will be handled explicitly upon request
            
            logging.info(f"User {user_id} connected to chat")
            
        except InvalidJWTToken:
            logging.info(f"Connection from {sid} failed due to invalid token")
            return False
        
        return True
    
    async def on_create_lesson_session(
        self, 
        sid: str, 
        data: dict,
        chat_service: ChatService = Depends()
    ):
        session = await self.get_session(sid)
        user_id = session.get("user_id", None)
        lesson_id = data.get("lesson_id", None)
        
        if not lesson_id:
            raise ValueError("Lesson ID not found")

        if not user_id:
            raise ValueError("User ID not found")

        chat_session, is_new_session = await chat_service.get_or_create_lesson_session(user_id, UUID(lesson_id))
        session["chat_session_id"] = chat_session.id
        
        if not is_new_session:
            await self.emit("continue_session", {"session_id": str(chat_session.id), "metadata": json.loads(chat_session.data or "{}")}, to=sid)
        else:
            await self.emit("start_session", {"session_id": str(chat_session.id)}, to=sid)

    async def on_disconnect(self, sid: str):
        """
        Handle client disconnection.

        Args:
            sid (str): Session ID.
        """
        logging.info(f"User disconnected from chat: {sid}")
        
        if sid in self.deepgram_connections:
            await self.deepgram_connections[sid].finish()
            del self.deepgram_connections[sid]

    # Message handling methods
    @inject_dependencies()
    async def on_send_message(self, sid: str, data: dict, chat_service: ChatService = Depends()):
        """
        Handle incoming messages from clients.

        Args:
            sid (str): Session ID.
            data (dict): Message data.
            chat_service (ChatService): Chat service dependency.
        """
        session = await self.get_session(sid)
        
        if session.get("producing_response", False):
            return
        
        user_id = session.get("user_id")
        prompt_type = session.get("prompt_type")
        use_voice = session.get("use_voice", False)
        instructor_id = session.get("instructor_id")
        chat_session_id = session.get("chat_session_id")
        
        if not prompt_type:
            raise ValueError("Prompt type not found")
        
        if not chat_session_id:
            raise ValueError("Chat session ID not found")
        
        session["producing_response"] = True
        
        async for chunk in chat_service.get_response(
            user_id=user_id,
            session_id=chat_session_id,
            instructor_id=instructor_id,
            prompt_type=prompt_type,
            message=data.get("message"),
            audio=data.get("audio"),
            expect_audio_response=use_voice,
            hide_from_chat=data.get("hide_from_chat", False)
        ):
            await self.emit("message_update", json.loads(chunk.model_dump_json()), to=sid)
        
        await self.emit("message_complete", to=sid)

        session["producing_response"] = False
        
    # Session management methods
    @inject_dependencies()
    async def on_set_instructor(
        self, 
        sid: str, 
        data: dict, 
        instructor_service: InstructorService = Depends(), 
        chat_service: ChatService = Depends(),
        user_service: UserService = Depends()
    ):
        """
        Set the instructor for a session.

        Args:
            sid (str): Session ID.
            data (dict): Data containing the instructor ID.
            chat_service (ChatService): Chat service dependency.
        """
        instructor_id = data.get("instructor_id")
        instructor = await instructor_service.get_instructor_by_id(UUID(instructor_id))
        
        if not instructor:
            raise ValueError("Instructor not found")
        
        session = await self.get_session(sid)
        session["instructor_id"] = instructor_id

        user = await user_service.get_user("id", session.get("user_id"))
        
        # Acknowledge the instructor change
        if user.default_instructor_id != instructor_id:
            await user_service.set_default_instructor(user.id, UUID(instructor_id))
            await chat_service.purge_session(session["chat_session_id"])
            await self.emit("purge_session", to=sid)
            
        await user_service.set_default_instructor(user.id, instructor.id)
        await self.emit("instructor_set", {"instructor_id": instructor_id}, to=sid)
        
        await self.on_send_message(sid, {"message": f"Hello, {instructor.name}!", "hide_from_chat": True}, chat_service)

    @inject_dependencies()
    async def on_set_prompt(self, sid: str, data: dict):
        """
        Set the prompt type for a session.

        Args:
            sid (str): Session ID.
            data (dict): Data containing the prompt type.
            chat_service (ChatService): Chat service dependency.
        """
        prompt_type = data.get("prompt_type")
        session = await self.get_session(sid)
        session["prompt_type"] = PromptType(prompt_type)
        
        chat_session_id = session.get("chat_session_id")
        
        if not chat_session_id:
            raise ValueError("Chat session ID not found")
        
        # Acknowledge the prompt change
        await self.emit("prompt_set", {"prompt_type": prompt_type}, to=sid)

    # Voice-related methods
    async def on_audio_data(self, sid: str, data: bytes):
        """
        Handle incoming audio data.

        Args:
            sid (str): Session ID.
            data (bytes): Audio data.
        """
        connection = self.deepgram_connections.get(sid)
        
        if not connection:
            return
        
        await connection.send(data)
        
    async def on_deepgram_message(self, connection: AsyncListenWebSocketClient, result: LiveResultResponse, **kwargs):
        """
        Handle Deepgram transcription messages.

        Args:
            connection (AsyncListenWebSocketClient): Deepgram connection.
            result (LiveResultResponse): Transcription result.
            **kwargs: Additional keyword arguments.
        """
        transcript = result.channel.alternatives[0].transcript
        
        if len(transcript) < 2:
            return
        
        await self.emit("voice_transcript", transcript, to=connection.sid)
        
    async def on_deepgram_utterance_end(self, connection: AsyncListenWebSocketClient, **kwargs):
        """
        Handle Deepgram utterance end.

        Args:
            connection (AsyncListenWebSocketClient): Deepgram connection.
            **kwargs: Additional keyword arguments.
        """
        await self.emit("voice_end", to=connection.sid)
        
    async def on_deepgram_error(self, connection: AsyncListenWebSocketClient, error: str, **kwargs):
        """
        Handle Deepgram errors.

        Args:
            connection (AsyncListenWebSocketClient): Deepgram connection.
            error (str): Error message.
            **kwargs: Additional keyword arguments.
        """
        logging.error(error)
        
    async def on_use_voice(self, sid: str, data: dict):
        """
        Enable or disable voice functionality for a session.

        Args:
            sid (str): Session ID.
            data (dict): Data containing the enabled flag.
        """
        enabled = data.get("enabled", False)
        sample_rate = data.get("sample_rate", 48000)
        
        session = await self.get_session(sid)
        session["use_voice"] = enabled
        
        if enabled:
            await self._setup_deepgram_connection(sid, sample_rate)
        elif not enabled and sid in self.deepgram_connections:
            await self._teardown_deepgram_connection(sid)

    # Helper methods
    async def _setup_deepgram_connection(self, sid: str, sample_rate: int):
        """Set up Deepgram connection for a session."""
        connection = self.deepgram_client.listen.asyncwebsocket.v("1")
        connection.sid = sid
        self.deepgram_connections[sid] = connection

        options = LiveOptions(
            punctuate=True,
            interim_results=True,
            language="en-US",
            smart_format=True,
            vad_events=True,
            sample_rate=sample_rate,
            channels=1,
            model="nova-2",
            encoding="linear16",
            utterance_end_ms=1000,
            endpointing=500
        )
        
        connection.on(LiveTranscriptionEvents.Transcript, self.on_deepgram_message)
        connection.on(LiveTranscriptionEvents.UtteranceEnd, self.on_deepgram_utterance_end)
        connection.on(LiveTranscriptionEvents.Error, self.on_deepgram_error)
        await connection.start(options)
        
        logging.info(f"Finished setting up Deepgram connection with sample rate {sample_rate}")

    async def _teardown_deepgram_connection(self, sid: str):
        """Tear down Deepgram connection for a session."""
        await self.deepgram_connections[sid].finish()
        del self.deepgram_connections[sid]
        
        logging.info("Finished tearing down Deepgram connection")