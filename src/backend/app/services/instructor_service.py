from typing import List, Optional
import uuid
from domain.schema.instructors import Instructor
from app.repositories.instructor_repository import InstructorRepository
from app.services.user_service import UserService
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
        if user and user.instructor_id:
            return await self.get_instructor_by_id(user.instructor_id)
        return None
