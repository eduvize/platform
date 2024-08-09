from fastapi import APIRouter, Depends, File, UploadFile

from domain.dto.profile import UserProfileDto
from .middleware.token_middleware import token_extractor, user_id_extractor
from app.services.user_onboarding_service import UserOnboardingService
from app.services.user_service import UserService
from domain.dto.user import UserDto

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(token_extractor), Depends(user_id_extractor)]
)

@router.get("/me", response_model=UserDto)
async def get_me(user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    current_user = await user_service.get_user("id", user_id)
    return current_user

@router.get("/me/onboarding")
async def get_onboarding_status(user_id: str = Depends(user_id_extractor), user_onboarding_service: UserOnboardingService = Depends(UserOnboardingService)):
    return await user_onboarding_service.get_onboarding_status(user_id)

@router.put("/me/profile")
async def update_profile(payload: UserProfileDto, user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    await user_service.update_profile(user_id, payload)
    
@router.post("/me/profile/avatar")
async def upload_avatar(file: UploadFile = File(...), user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    await user_service.upload_avatar(user_id, file)

@router.get("/{username}")
async def get_user(username: str, user_service: UserService = Depends(UserService)):
    details = await user_service.get_user("username", username)
    return UserDto.model_validate(details)
