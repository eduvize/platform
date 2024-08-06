from fastapi import APIRouter, Depends, File, UploadFile
from app.ai.prompts.resume_scan.resume_scanner_prompt import ResumeScannerPrompt
from app.common.conversion.pdf_to_image import get_images_from_pdf_bytes
from app.routing.middleware.token_middleware import token_extractor, user_id_extractor

router = APIRouter(
    prefix="/files",
    dependencies=[
        Depends(token_extractor),
        Depends(user_id_extractor)
    ]
)

@router.post("/resume")
async def get_resume_details(file: UploadFile = File(...)):
    images = get_images_from_pdf_bytes(await file.read())
    
    return ResumeScannerPrompt().get_profile_data(images)