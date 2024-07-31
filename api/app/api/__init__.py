from fastapi import APIRouter

api_router = APIRouter()

from .user_router import router as user_router
from .auth_router import router as auth_router

api_router.include_router(auth_router)
api_router.include_router(user_router)