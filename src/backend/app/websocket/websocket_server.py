import logging
from socketio import AsyncServer
from .playground.playground_namespace import PlaygroundNamespace
from .chat.chat_namespace import ChatNamespace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Increase max payload size (e.g., to 5MB)
socket_server = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    async_handlers=True,
    max_http_buffer_size=5 * 1024 * 1024  # 5MB in bytes
)

# Register the namespace
socket_server.register_namespace(PlaygroundNamespace('/playground'))
socket_server.register_namespace(ChatNamespace('/chat'))
