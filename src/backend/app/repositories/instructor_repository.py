import uuid
from sqlmodel import Session, select
from domain.schema.instructor.instructor import Instructor
from domain.dto.instructor import InstructorDto
from common.database import engine

class InstructorRepository:
    async def create_instructor(self, user_id: uuid.UUID, instructor: InstructorDto):
        """
        Creates an instructor record for a user in the database

        Args:
            user_id (uuid.UUID): The ID of the user to associate the instructor with
            instructor (InstructorDto): _description_
        """
        
        with Session(engine) as session:
            instructor = Instructor(
                user_id=user_id,
                name=instructor.name,
                avatar_url=instructor.avatar_url
            )
            
            session.add(instructor)
            session.commit()
            session.refresh(instructor)
            
    async def update_instructor(self, user_id: uuid.UUID, instructor_dto: InstructorDto):
        """
        Updates an existing instructor record in the database

        Args:
            user_id (uuid.UUID): The ID of the user to associate the instructor with
            instructor (InstructorDto): The updated instructor data
        """
        
        with Session(engine) as session:
            instructor_query = select(Instructor).where(Instructor.user_id == user_id)
            resultset = session.exec(instructor_query)
            
            instructor = resultset.first()
            
            instructor.name = instructor_dto.name
            instructor.avatar_url = instructor_dto.avatar_url
            
            session.commit()
            
    async def approve_instructor(self, user_id: uuid.UUID):
        """
        Approves an instructor for the user

        Args:
            user_id (uuid.UUID): The ID of the user whose instructor status is to be approved
        """
        
        with Session(engine) as session:
            instructor_query = select(Instructor).where(Instructor.user_id == user_id)
            resultset = session.exec(instructor_query)
            
            instructor = resultset.first()
            
            instructor.is_approved = True
            
            session.commit()