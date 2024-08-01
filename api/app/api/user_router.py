from fastapi import APIRouter, Depends

from app.api.middleware.token_middleware import token_extractor, user_id_extractor
from app.models.dto.user import UserDto

from ..services import get_user_service
from ..services.users import UserService

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(token_extractor), Depends(user_id_extractor)]
)

@router.get("/me")
async def get_me(user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    current_user = await user_service.get_user_by_id(user_id)
    return UserDto.model_validate(current_user)

@router.get("/{username}")
async def get_user(username: str, user_service: UserService = Depends(get_user_service)):
    details = await user_service.get_user_by_name(username)
    return UserDto.model_validate(details)