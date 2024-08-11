from fastapi import APIRouter, Depends, File, Response, UploadFile
from .middleware import token_extractor, user_id_extractor
from app.services import UserService, UserOnboardingService

from app.utilities.profile import get_user_profile_text
from domain.dto.profile import UserProfileDto
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
    
@router.get("/me/profile/text", response_class=Response)
async def get_me_profile_text(user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    current_user = await user_service.get_user("id", user_id)
    profile_text = get_user_profile_text(UserProfileDto.from_orm(current_user.profile))
    return Response(content=profile_text, media_type="text/plain")
    
@router.post("/me/profile/avatar")
async def upload_avatar(file: UploadFile = File(...), user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    await user_service.upload_avatar(user_id, file)

@router.get("/{username}")
async def get_user(username: str, user_service: UserService = Depends(UserService)):
    details = await user_service.get_user("username", username)
    return UserDto.model_validate(details)
