from fastapi import FastAPI
import socketio
import asyncio
import subprocess
import os

# Create a new Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi')

# Create a new FastAPI app
app = FastAPI()

# Attach the Socket.IO server to the FastAPI app
app.mount('/', socketio.ASGIApp(sio))

# A dictionary to hold shell processes per client
clients = {}

# Define a handler for the connect event
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('message', {'data': 'Welcome!'}, to=sid)

    # Start a persistent shell process for this client
    process = await asyncio.create_subprocess_shell(
        'bash --rcfile /playground-hidden/.bashrc',
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/userland"
    )

    # Store the process in the clients dictionary
    clients[sid] = process

    # Make a file at /userland/ with the sid
    with open(f"/userland/{sid}.txt", "w") as f:
        f.write("Hello, World!")

# Define a handler for the disconnect event
@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

    # Terminate the shell process for this client
    process = clients.pop(sid, None)
    if process:
        process.terminate()
        await process.wait()

# Define a handler for a custom event to execute shell commands
@sio.event
async def execute_command(sid, data):
    command = data.get('command', None)
    if not command:
        await sio.emit('message', {'data': 'No command provided'}, to=sid)
        return

    # Get the persistent shell process for this client
    process = clients.get(sid)
    if not process:
        await sio.emit('message', {'data': 'No active shell session'}, to=sid)
        return

    # Send the command to the shell
    process.stdin.write(command.encode() + b'\n')
    await process.stdin.drain()

    # Read the output from the shell process
    async def stream_output(stream, event_name):
        while True:
            line = await stream.readline()
            if not line:
                break
            await sio.emit(event_name, {'data': line.decode().strip()}, to=sid)

    await asyncio.gather(
        stream_output(process.stdout, 'stdout'),
        stream_output(process.stderr, 'stderr')
    )

# Define a custom event for handling generic messages
@sio.event
async def custom_event(sid, data):
    print(f"Message from {sid}: {data}")
    await sio.emit('message', {'data': 'Message received'}, to=sid)