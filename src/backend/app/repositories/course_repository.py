from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import update
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from domain.schema.courses import Course, Module, Lesson, Section, CourseExercise, CourseExerciseObjective
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
            added_lessons = []
            
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
                    
                    added_lessons.append(lesson_entity)
                    
                    section_index = 0
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
            session.refresh(course_entity)
            
            # Set the first lesson as the current lesson
            course_entity.current_lesson_id = added_lessons[0].id
            
            # save the course entity
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
            
    def set_current_lesson(
        self,
        course_id: uuid.UUID,
        lesson_id: uuid.UUID,
        section_index: int
    ) -> None:
        with Session(engine) as session:
            update_query = (
                update(Course)
                .where(Course.id == course_id)
                .values(current_lesson_id=lesson_id, lesson_index=section_index)
            )
            
            session.exec(update_query)
            session.commit()
            
    def set_course_completion(
        self,
        course_id: uuid.UUID
    ) -> None:
        with Session(engine) as session:
            update_query = (
                update(Course)
                .where(Course.id == course_id)
                .values(completed_at_utc=datetime.utcnow())
            )
            
            session.exec(update_query)
            session.commit()
            
    def get_next_lesson(
        self,
        course_id: uuid.UUID,
        current_lesson_id: uuid.UUID
    ) -> Optional[Lesson]:
        with Session(engine) as session:
            course_query = (
                select(Course)
                .where(Course.id == course_id)
                .options(
                    joinedload(Course.modules)
                    .joinedload(Module.lessons)
                )
            )
            
            resultset = session.exec(course_query)
            course = resultset.first()
            
            if course is None:
                raise ValueError("Course not found")
            
            current_lesson = next((
                lesson
                for module in course.modules
                for lesson in module.lessons
                if lesson.id == current_lesson_id
            ), None)
            
            if current_lesson is None:
                raise ValueError("Current lesson not found")
            
            next_lesson_in_module = next((
                lesson
                for module in course.modules
                for lesson in module.lessons
                if lesson.module_id == current_lesson.module_id and lesson.order == current_lesson.order + 1
            ), None)
            
            if next_lesson_in_module:
                return next_lesson_in_module
            
            next_module = next((
                module
                for module in course.modules
                if module.order == current_lesson.module.order + 1
            ), None)
            
            if next_module:
                return next_module.lessons[0]
            
            return None
            
    def get_courses(self, user_id: uuid.UUID) -> list[Course]:
        with Session(engine) as session:
            query = (
                select(Course)
                .where(Course.user_id == user_id)
                .options(
                    joinedload(Course.modules)
                    .joinedload(Module.lessons)
                    .joinedload(Lesson.sections)
                )
                .order_by(Course.created_at_utc, Course.title)
            )
            
            resultset = session.exec(query).unique()
            courses = resultset.all()
            
            return courses
        
    def get_lesson_count(self, course_id: uuid.UUID) -> int:
        with Session(engine) as session:
            query = (
                select(Lesson.id)
                .join(Module, Lesson.module_id == Module.id)
                .where(Module.course_id == course_id)
            )
            
            resultset = session.exec(query)
            lessons = resultset.all()
            
            return len(lessons)
        
    def get_lesson(self, lesson_id: uuid.UUID) -> Optional[Lesson]:
        with Session(engine) as session:
            query = (
                select(Lesson)
                .where(Lesson.id == lesson_id)
                .options(
                    joinedload(Lesson.sections),
                    joinedload(Lesson.exercises)
                    .joinedload(CourseExercise.objectives)
                )
            )
            
            resultset = session.exec(query)
            lesson = resultset.first()
            
            return lesson
        
    def get_course(self, course_id: uuid.UUID) -> Optional[Course]:
        with Session(engine) as session:
            query = (
                select(Course)
                .where(Course.id == course_id)
                .options(
                    joinedload(Course.modules)
                    .joinedload(Module.lessons)
                    .joinedload(Lesson.sections),
                    joinedload(Course.modules)
                    .joinedload(Module.lessons)
                    .joinedload(Lesson.exercises)
                    .joinedload(CourseExercise.objectives),
                )
            )
            
            resultset = session.exec(query)
            course = resultset.first()
            
            if course is None:
                return None
            
            # Order by module, lesson, section "order" field
            course.modules.sort(key=lambda x: x.order)
            for module in course.modules:
                module.lessons.sort(key=lambda x: x.order)
                for lesson in module.lessons:
                    lesson.sections.sort(key=lambda x: x.order)
                    
            return course
        
    def create_exercise(
        self,
        lesson_id: uuid.UUID, 
        environment_id: uuid.UUID, 
        title: str, 
        summary: str, 
        objectives: list[str]
    ) -> uuid.UUID:
        with Session(engine) as session:
            exercise_entity = CourseExercise(
                lesson_id=lesson_id,
                title=title,
                environment_id=environment_id,
                summary=summary
            )
            
            session.add(exercise_entity)
            
            for objective in objectives:
                objective_entity = CourseExerciseObjective(
                    objective=objective,
                    exercise_id=exercise_entity.id
                )
                
                session.add(objective_entity)
            
            session.commit()
            session.refresh(exercise_entity)
            
            return exercise_entity.id
        
    def set_exercise_environment(self, exercise_id: uuid.UUID, environment_id: uuid.UUID) -> None:
        with Session(engine) as session:
            update_query = (
                update(CourseExercise)
                .where(CourseExercise.id == exercise_id)
                .values(environment_id=environment_id)
            )
            
            session.exec(update_query)
            session.commit()
            
    def get_exercise_by_environment(self, environment_id: uuid.UUID) -> Optional[CourseExercise]:
        with Session(engine) as session:
            query = (
                select(CourseExercise)
                .where(CourseExercise.environment_id == environment_id)
                .options(
                    joinedload(CourseExercise.objectives)
                )
            )
            
            resultset = session.exec(query)
            exercise = resultset.first()
            
            return exercise
            
    def remove_exercise(self, exercise_id: uuid.UUID) -> None:
        """
        Removes an exercise and its objectives from the database

        Args:
            exercise_id (uuid.UUID): The ID of the exercise to remove
        """
        
        with Session(engine) as session:
            query = (
                select(CourseExercise)
                .where(CourseExercise.id == exercise_id)
            )
            
            resultset = session.exec(query)
            exercise = resultset.first()
            
            if exercise is None:
                raise ValueError("Exercise not found")
            
            session.delete(exercise)
            session.commit()