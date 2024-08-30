from typing import Optional
import uuid

from sqlalchemy import update
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
                cover_image_url=course_dto.cover_image_url,
                user_id=user_id
            )
            
            session.add(course_entity)
            session.commit()
            session.refresh(course_entity)
            
            return course_entity.id
        
    def create_course_content(
        self,
        course_id: uuid.UUID,
        course_dto: CourseDto
    ):
        with Session(engine) as session:
            query = (
                select(Course)
                .where(Course.id == course_id)
            )
            resultset = session.exec(query)
            
            course_entity = resultset.first()
            
            if course_entity is None:
                raise ValueError("Course not found")
            
            course_entity.is_generating = False
            course_entity.generation_progress = 100
            
            module_index = 0
            lesson_index = 0
            section_index = 0
            
            for module_dto in course_dto.modules:
                module_entity = Module(
                    title=module_dto.title,
                    description=module_dto.description,
                    course_id=course_entity.id,
                    order=module_index
                )
                module_index += 1
                
                session.add(module_entity)
                
                for lesson_dto in module_dto.lessons:
                    lesson_entity = Lesson(
                        title=lesson_dto.title,
                        description=lesson_dto.description,
                        module_id=module_entity.id,
                        order=lesson_index
                    )
                    lesson_index += 1
                    
                    session.add(lesson_entity)
                    
                    for section_dto in lesson_dto.sections:
                        section_entity = Section(
                            title=section_dto.title,
                            description=section_dto.description,
                            content=section_dto.content,
                            lesson_id=lesson_entity.id,
                            order=section_index
                        )
                        section_index += 1
                        
                        session.add(section_entity)
                        
            session.commit()
            
    def set_generation_progress(
        self,
        course_id: uuid.UUID,
        progress: int
    ) -> None:
        with Session(engine) as session:
            update_query = (
                update(Course)
                .where(Course.id == course_id)
                .values(generation_progress=progress)
            )
            
            session.exec(update_query)
            session.commit()
            
    def get_courses(self, user_id: uuid.UUID) -> list[Course]:
        with Session(engine) as session:
            query = (
                select(Course)
                .where(Course.user_id == user_id)
                .order_by(Course.created_at, Course.title)
            )
            
            resultset = session.exec(query)
            courses = resultset.all()
            
            return courses
        
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
                .order_by(Module.order, Lesson.order, Section.order)
            )
            
            resultset = session.exec(query)
            course = resultset.first()
            
            return course