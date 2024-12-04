from fastapi import APIRouter, Depends, File, UploadFile
from .middleware import token_validator, user_id_extractor
from app.services import UserService, UserOnboardingService
from domain.dto.user import UserDto

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(token_validator), Depends(user_id_extractor)]
)

@router.get("/me", response_model=UserDto)
async def get_me(
    user_id: str = Depends(user_id_extractor), 
    user_service: UserService = Depends(UserService)
):
    current_user = await user_service.get_user(
        by="id", 
        value=user_id
    )
    
    return current_user

@router.get("/me/onboarding")
async def get_onboarding_status(
    user_id: str = Depends(user_id_extractor), 
    user_onboarding_service: UserOnboardingService = Depends(UserOnboardingService)
):
    return await user_onboarding_service.get_onboarding_status(
        user_id=user_id
    )
    
@router.post("/me/profile/avatar")
async def upload_avatar(
    file: UploadFile = File(...), 
    user_id: str = Depends(user_id_extractor), 
    user_service: UserService = Depends(UserService)
):
    await user_service.upload_avatar(
        user_id=user_id, 
        file=file
    )

@router.get("/{username}")
async def get_user(
    username: str, 
    user_service: UserService = Depends(UserService)
):
    details = await user_service.get_user("username", username)
    return UserDto.model_validate(details)
