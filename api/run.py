import os
import uvicorn
from dotenv import load_dotenv
from app import app

load_dotenv()

APP_PORT = os.getenv("PORT", 8000)
LIVE_RELOAD = os.getenv("ENABLE_LIVE_RELOAD", "true")

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=int(APP_PORT), reload=bool(LIVE_RELOAD))