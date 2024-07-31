from fastapi import APIRouter, Depends

from app.models.dto.user import UserDto

from ..services import get_user_service
from ..services.users import UserService

router = APIRouter(prefix="/users")

@router.api_route("/me")
async def get_me():
    return {"username": "fakecurrentuser"}

@router.api_route("/{username}")
async def get_user(username: str, user_service: UserService = Depends(get_user_service)):
    details = user_service.get_user_by_name(username)
    return UserDto.model_validate(details)