import base64
from typing import List, Optional
import uuid
from domain.schema.instructors import Instructor
from app.repositories.instructor_repository import InstructorRepository
from app.services.user_service import UserService
from common.cache import get_key, set_key
from fastapi import Depends

class InstructorService:
    def __init__(
        self,
        instructor_repository: InstructorRepository = Depends(InstructorRepository),
        user_service: UserService = Depends(UserService)
    ):
        self.instructor_repository = instructor_repository
        self.user_service = user_service

    async def get_all_instructors(self) -> List[Instructor]:
        """
        Retrieves all instructors.

        Returns:
            List[Instructor]: A list of all instructor records.
        """
        return await self.instructor_repository.get_all_instructors()

    async def get_instructor_by_id(self, instructor_id: uuid.UUID) -> Optional[Instructor]:
        """
        Retrieves a specific instructor by their ID.

        Args:
            instructor_id (uuid.UUID): The ID of the instructor to retrieve.

        Returns:
            Optional[Instructor]: The instructor record if found, otherwise None.
        """
        return await self.instructor_repository.get_instructor_by_id(instructor_id)

    async def get_user_instructor(self, user_id: uuid.UUID) -> Optional[Instructor]:
        """
        Retrieves the instructor associated with a specific user.

        Args:
            user_id (uuid.UUID): The ID of the user whose instructor to retrieve.

        Returns:
            Optional[Instructor]: The instructor record if found, otherwise None.
        """
        user = await self.user_service.get_user("id", user_id)
        if user and user.default_instructor_id:
            return await self.get_instructor_by_id(user.default_instructor_id)
        return None

    async def get_instructor_profile_photo(self, instructor_id: uuid.UUID) -> bytes:
        """
        Retrieves the profile photo URL for a specific instructor.

        Args:
            instructor_id (uuid.UUID): The ID of the instructor to retrieve the profile photo for.

        Returns:
            Optional[str]: The URL of the profile photo if found, otherwise None.
        """

        
        # Check the cache first
        cache_key = f"instructor_profile_photo:{instructor_id}"
        cached_photo = await get_key(cache_key)
        if cached_photo:
            # Return the cached base64 as bytes
            return base64.b64decode(cached_photo)
        
        # If not cached, fetch from database
        instructor = await self.instructor_repository.get_instructor_by_id(instructor_id)
        
        if not instructor:
            raise ValueError(f"Instructor with ID {instructor_id} not found")
        
        b64_image = _strip_data_url(instructor.image_url)
        
        # Cache the result
        await set_key(cache_key, b64_image)
        
        return base64.b64decode(b64_image)

def _strip_data_url(data_url: str) -> str:
    """
    Strips the data URL prefix and returns the base64 encoded image.

    Args:
        data_url (str): The data URL containing the base64 encoded image.

    Returns:
        str: The base64 encoded image.
    """
    
    # Extract the base64 part from the data URL
    if data_url.startswith('data:image'):
        # Split the string and get the base64 part
        base64_data = data_url.split(',')[1]
        return base64_data
    else:
        # If it's not a data URL, return the original string
        return data_url