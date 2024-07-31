from fastapi import FastAPI
from .websocket import websocket_router
from .api import api_router

app = FastAPI()

app.include_router(api_router)
app.include_router(websocket_router)