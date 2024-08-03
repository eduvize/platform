from fastapi import FastAPI
from socketio import ASGIApp
from .routing import api_router
from .websocket import socket
from starlette.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
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

socket_app = ASGIApp(socket, socketio_path="socket.io")

app.mount("/socket.io", socket_app)