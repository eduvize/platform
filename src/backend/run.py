import os
import uvicorn
from dotenv import load_dotenv
from app.main import socket_app

load_dotenv()

APP_PORT = os.getenv("PORT", 8000)

if __name__ == "__main__":
    uvicorn.run("run:socket_app", host="0.0.0.0", port=int(APP_PORT), workers=1)