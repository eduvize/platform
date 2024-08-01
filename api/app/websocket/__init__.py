from app import sio

@sio.event
async def connect(sid, data):
    print(f"Client {sid} connected")