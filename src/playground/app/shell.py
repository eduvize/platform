import asyncio
import socketio
from asyncio import subprocess

class Shell:
    owner_id: str
    server: socketio.AsyncServer
    process: subprocess.Process
    
    def __init__(self, owner_id: str, server: socketio.AsyncServer):
        self.owner_id = owner_id
        self.server = server
        
    async def start(self):
        self.process = await asyncio.create_subprocess_shell(
            'bash --rcfile /playground-hidden/.bashrc',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/userland"
        )
        
        await asyncio.gather(
            self.stream_output(self.process.stdout, 'stdout'),
            self.stream_output(self.process.stderr, 'stderr')
        )
        
    async def terminate(self):
        self.process.terminate()
        await self.process.wait()
        
    async def execute_command(self, command: str):
        self.process.stdin.write(command.encode() + b'\n')
        await self.process.stdin.drain()
        
    async def stream_output(self, stream, event_name):
        while True:
            line = await stream.readline()
            if not line:
                break
            await self.server.emit(event_name, {'data': line.decode().strip()}, to=self.owner_id)