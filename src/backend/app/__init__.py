from fastapi import FastAPI
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