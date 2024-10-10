from typing import List, Optional
import uuid
from sqlmodel import select
from domain.schema.instructors import Instructor
from common.database import AsyncSession, async_engine

class InstructorRepository:
    """
    Handles data access operations for Instructor records in the database
    """

    async def get_all_instructors(self) -> List[Instructor]:
        """
        Retrieves all instructors from the database

        Returns:
            List[Instructor]: A list of all instructor records
        """
        async with AsyncSession(async_engine) as session:
            query = select(Instructor)
            result = await session.exec(query)
            return result.all()

    async def get_instructor_by_id(self, instructor_id: uuid.UUID) -> Optional[Instructor]:
        """
        Retrieves a specific instructor by their ID

        Args:
            instructor_id (str): The ID of the instructor to retrieve

        Returns:
            Optional[Instructor]: The instructor record if found, otherwise None
        """
        async with AsyncSession(async_engine) as session:
            query = select(Instructor).where(Instructor.id == instructor_id)
            result = await session.exec(query)
            return result.one_or_none()