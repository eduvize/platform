from typing import Optional
import uuid

from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from domain.schema.courses import Course, Module, Lesson, Section
from domain.dto.courses.course import CourseDto
from common.database import engine

class CourseRepository:
    def create_course(
        self,
        user_id: uuid.UUID,
        course_dto: CourseDto
    ):
        with Session(engine) as session:
            course_entity = Course(
                title=course_dto.title,
                description=course_dto.description,
                user_id=user_id
            )
            
            session.add(course_entity)
            
            for module_dto in course_dto.modules:
                module_entity = Module(
                    title=module_dto.title,
                    description=module_dto.description,
                    course_id=course_entity.id
                )
                
                session.add(module_entity)
                
                for lesson_dto in module_dto.lessons:
                    lesson_entity = Lesson(
                        title=lesson_dto.title,
                        description=lesson_dto.description,
                        module_id=module_entity.id
                    )
                    
                    session.add(lesson_entity)
                    
                    for section_dto in lesson_dto.sections:
                        section_entity = Section(
                            title=section_dto.title,
                            description=section_dto.description,
                            content=section_dto.content,
                            lesson_id=lesson_entity.id
                        )
                        
                        session.add(section_entity)
                        
            session.commit()
            
            return course_entity.id
        
    def get_course(self, user_id: uuid.UUID, course_id: uuid.UUID) -> Optional[Course]:
        with Session(engine) as session:
            query = (
                select(Course)
                .where(Course.id == course_id and Course.user_id == user_id)
                .options(
                    joinedload(Course.modules)
                    .joinedload(Module.lessons)
                    .joinedload(Lesson.sections)
                )
            )
            
            resultset = session.exec(query)
            course = resultset.first()
            
            return course