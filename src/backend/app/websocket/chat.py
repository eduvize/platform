import json
import logging
from uuid import UUID
from fastapi import Depends
from socketio import AsyncNamespace
from app.services.chat_service import ChatService
from app.services.user_service import UserService
from app.utilities.jwt import decode_token, InvalidJWTToken
from domain.enums.chat_enums import PromptType
from config import get_token_secret, get_deepgram_api_key
from .dependency_resolver import inject_dependencies
from .util import get_token_from_environ
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
    async def on_connect(self, sid: str, environ: dict, user_service: UserService = Depends(), chat_service: ChatService = Depends()):
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
            user_id = decoded["id"]
            
            session = await self.get_session(sid)
            session["user_id"] = user_id
            
            user = await user_service.get_user("id", user_id)
            
            if not user.default_instructor_id:
                raise ValueError("User does not have a default instructor")
            
            session["instructor_id"] = user.default_instructor_id
            
            chat_session = await chat_service.create_session(user_id=user_id)
            
            session["chat_session_id"] = chat_session.id
            
            logging.info(f"User {user_id} connected to chat")
            
        except InvalidJWTToken:
            logging.info(f"Connection from {sid} failed due to invalid token")
            return False
        
        return True

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

    # Session management methods
    async def on_set_instructor(self, sid: str, data: dict):
        """
        Set the instructor for a session.

        Args:
            sid (str): Session ID.
            data (dict): Data containing the instructor ID.
        """
        instructor_id = data.get("instructor_id")
        session = await self.get_session(sid)
        session["instructor_id"] = instructor_id
        
    @inject_dependencies()
    async def on_set_prompt(self, sid: str, data: dict, chat_service: ChatService = Depends()):
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
        is_final = result.is_final
        
        if not transcript:
            return
        
        await self.emit("voice_transcript", transcript, to=connection.sid)
        
        if is_final:
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
            encoding="linear16"
        )
        
        connection.on(LiveTranscriptionEvents.Transcript, self.on_deepgram_message)
        connection.on(LiveTranscriptionEvents.Error, self.on_deepgram_error)
        await connection.start(options)
        
        logging.info(f"Finished setting up Deepgram connection with sample rate {sample_rate}")

    async def _teardown_deepgram_connection(self, sid: str):
        """Tear down Deepgram connection for a session."""
        await self.deepgram_connections[sid].finish()
        del self.deepgram_connections[sid]
        
        logging.info("Finished tearing down Deepgram connection")