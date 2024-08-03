from fastapi import APIRouter, Depends, File, UploadFile

from .contracts.file_contracts import FileUploadResponse
from .contracts.user_contracts import UpdateProfilePayload
from .middleware.token_middleware import token_extractor, user_id_extractor
from ..models.dto.user import UserDto

from ..services.user_service import UserService

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(token_extractor), Depends(user_id_extractor)]
)

@router.get("/me")
async def get_me(user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    current_user = await user_service.get_user("id", user_id)
    return UserDto.model_validate(current_user)

@router.put("/me/profile")
async def update_profile(payload: UpdateProfilePayload, user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    await user_service.update_profile(user_id, payload)
    
@router.post("/me/profile/avatar")
async def upload_avatar(file: UploadFile = File(...), user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    object_id = await user_service.upload_avatar(user_id, file)
    
@router.get("/{username}")
async def get_user(username: str, user_service: UserService = Depends(UserService)):
    details = await user_service.get_user("username", username)
    return UserDto.model_validate(details)


    
    return FileUploadResponse.model_construct(file_id=object_id)