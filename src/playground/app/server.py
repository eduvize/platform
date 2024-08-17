import socketio
from typing import Dict
from fastapi import FastAPI
from .shell import Shell

sio = socketio.AsyncServer(async_mode='asgi')
app = FastAPI()
app.mount('/', socketio.ASGIApp(sio))

clients: Dict[str, Shell] = {}

# Define a handler for the connect event
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    clients[sid] = Shell(sid, sio)
    
    await clients[sid].start()

# Define a handler for the disconnect event
@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

    shell = clients.pop(sid)
    
    if shell:
        await shell.terminate()

# Define a handler for a custom event to execute shell commands
@sio.event
async def execute_command(sid, command):
    await clients[sid].execute_command(command)