from fastapi import APIRouter

api_router = APIRouter()

from .onboarding_router import router as onboarding_router
from .user_router import router as user_router
from .auth_router import router as auth_router
from .autocomplete_router import router as autocomplete_router
from .file_router import router as file_router
from .validation_router import router as validation_router
from .chat_router import router as chat_router
from .playground_router import router as playground_router
from .course_router import router as course_router

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(onboarding_router)
api_router.include_router(autocomplete_router)
api_router.include_router(file_router)
api_router.include_router(validation_router)
api_router.include_router(chat_router)
api_router.include_router(playground_router)
api_router.include_router(course_router)