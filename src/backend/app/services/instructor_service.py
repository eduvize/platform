from fastapi import Depends
from openai import OpenAI
from app.repositories import InstructorRepository
from domain.dto.instructor.instructor import InstructorDto
from config import get_openai_key

class InstructorService:
    openai: OpenAI
    
    def __init__(self, instructor_repository: InstructorRepository = Depends(InstructorRepository)):
        self.instructor_repository = instructor_repository
        self.openai = OpenAI(api_key=get_openai_key())
        
    async def generate_instructor(self, animal_name: str) -> InstructorDto:
        response = self.openai.images.generate(
            model="dall-e-3",
            prompt=f"Icon of a cute {animal_name} head in metallic rainbow iridescent material, 3D render isometric perspective rendered in Cinema 4D on dark background",
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return InstructorDto.model_construct(
            avatar_url=response.data[0].url
        )