from fastapi import FastAPI
from socketio import ASGIApp
from app.routing import api_router
from app.websocket import socket
from starlette.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "https://eduvize.dev"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

socket_app = ASGIApp(
    socketio_server=socket, 
    other_asgi_app=app,
    socketio_path="socket.io"
)
