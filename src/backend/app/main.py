from . import app
from socketio import ASGIApp
from app.routing import api_router
from app.websocket import socket_server

app.include_router(api_router, prefix="/api")

socket_app = ASGIApp(
    socketio_server=socket_server, 
    other_asgi_app=app,
    socketio_path="socket.io",
)
