from fastapi import APIRouter, Depends

from ..services import get_user_service
from ..services.users import UserService
from . import api_router

router = APIRouter(prefix="/users")

@router.api_route("/me")
async def get_me():
    return {"username": "fakecurrentuser"}

@router.api_route("/{username}")
async def get_user(username: str, user_service: UserService = Depends(get_user_service)):
    return user_service.get_user(username)