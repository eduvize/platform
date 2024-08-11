from fastapi import Depends
from openai import OpenAI
from app.repositories import InstructorRepository
from ai.prompts import CreateInstructorProfilePrompt
from app.services.user_service import UserService
from domain.dto.instructor.instructor import InstructorDto
from common.storage import StoragePurpose, get_public_object_url, import_from_url
from config import get_openai_key

class InstructorNotFoundError(Exception):
    def __repr__(self):
        return "No instructor found for user"

class InstructorService:
    openai: OpenAI
    user_service: UserService
    instructor_repo: InstructorRepository
    
    def __init__(
        self, 
        instructor_repository: InstructorRepository = Depends(InstructorRepository),
        user_service: UserService = Depends(UserService)
    ):
        self.user_service = user_service
        self.instructor_repo = instructor_repository
        self.openai = OpenAI(api_key=get_openai_key())
        
    async def get_instructor(self, user_id: str) -> InstructorDto:
        user = await self.user_service.get_user("id", user_id, ["instructor"])
        
        if user is None:
            raise ValueError("User not found")
        
        if user.instructor is None:
            raise InstructorNotFoundError()
        
        return user.instructor
        
    async def generate_instructor(self, user_id: str, animal_name: str) -> InstructorDto:
        user = await self.user_service.get_user("id", user_id, ["instructor"])
        
        if user is None:
            raise ValueError("User not found")
        
        print(user)
        
        response = self.openai.images.generate(
            model="dall-e-3",
            prompt=f"Icon of a cute {animal_name} head in metallic rainbow iridescent material, 3D render isometric perspective rendered in Cinema 4D on dark background",
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        response_url = response.data[0].url
        
        creation_prompt = CreateInstructorProfilePrompt()
        profile = creation_prompt.get_profile(animal_name)
        
        object_id = await import_from_url(
            url=response_url,
            purpose=StoragePurpose.INSTRUCTOR_ASSET
        )
        
        public_url = get_public_object_url(
            purpose=StoragePurpose.INSTRUCTOR_ASSET,
            object_id=object_id
        )
        
        profile.avatar_url = public_url
        
        if user.instructor is None:
            await self.instructor_repo.create_instructor(user.id, profile)
        else:
            await self.instructor_repo.update_instructor(user.id, profile)
        
        return profile