from fastapi import APIRouter, Depends, File, UploadFile

from ai.prompts.resume_scan.resume_scanner_prompt import ResumeScannerPrompt

from .middleware.token_middleware import token_extractor, user_id_extractor
from .contracts.user_contracts import UpdateProfilePayload
from .contracts.file_contracts import FileUploadResponse
from common.conversion.pdf_to_image import get_images_from_pdf_bytes
from app.services.user_onboarding_service import UserOnboardingService
from app.services.user_service import UserService
from domain.dto.user import UserDto

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(token_extractor), Depends(user_id_extractor)]
)

@router.get("/me")
async def get_me(user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    current_user = await user_service.get_user("id", user_id)
    return UserDto.model_validate(current_user)

@router.get("/me/onboarding")
async def get_onboarding_status(user_id: str = Depends(user_id_extractor), user_onboarding_service: UserOnboardingService = Depends(UserOnboardingService)):
    return await user_onboarding_service.get_onboarding_status(user_id)

@router.put("/me/profile")
async def update_profile(payload: UpdateProfilePayload, user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    await user_service.update_profile(user_id, payload)
    
@router.post("/me/profile/avatar")
async def upload_avatar(file: UploadFile = File(...), user_id: str = Depends(user_id_extractor), user_service: UserService = Depends(UserService)):
    object_id = await user_service.upload_avatar(user_id, file)
    return FileUploadResponse.model_construct(file_id=object_id)

@router.get("/{username}")
async def get_user(username: str, user_service: UserService = Depends(UserService)):
    details = await user_service.get_user("username", username)
    return UserDto.model_validate(details)
