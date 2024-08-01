from fastapi import FastAPI
from .websocket import websocket_router
from .routing import api_router

app = FastAPI()

app.include_router(api_router, prefix="/api")
app.include_router(websocket_router, prefix="/ws")