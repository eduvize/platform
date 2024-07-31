from fastapi import APIRouter

api_router = APIRouter()

from .user_router import router as user_router

api_router.include_router(user_router)