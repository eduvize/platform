from fastapi import FastAPI
from socketio import ASGIApp
from .routing import api_router
from .websocket import socket

fastapi_app = FastAPI()
fastapi_app.include_router(api_router, prefix="/api")

app = ASGIApp(socket, fastapi_app, socketio_path="socket.io")