from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import update
from sqlmodel import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from domain.schema.courses import Course, Module, Lesson, Section, CourseExercise, CourseExerciseObjective
from domain.dto.courses.course import CourseDto
from domain.dto.courses.exercise_plan import ExerciseObjectivePlan
from common.database import get_async_session

class CourseRepository:
    async def create_course(
        self,
        user_id: uuid.UUID,
        course_dto: CourseDto
    ):
        async for session in get_async_session():
            course_entity = Course(
                title=course_dto.title,
                description=course_dto.description,
                cover_image_url=course_dto.cover_image_url,
                user_id=user_id
            )
            
            session.add(course_entity)
            await session.commit()
            await session.refresh(course_entity)
            
            return course_entity.id
        
    async def create_course_content(
        self,
        course_id: uuid.UUID,
        course_dto: CourseDto
    ):
        async for session in get_async_session():
            query = (
                select(Course)
                .where(Course.id == course_id)
            )
            result = await session.execute(query)
            course_entity = result.scalar_one_or_none()
            
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
                        
            await session.commit()
            await session.refresh(course_entity)
            
            # Set the first lesson as the current lesson
            course_entity.current_lesson_id = added_lessons[0].id
            
            # save the course entity
            await session.commit()
            
    async def set_generation_progress(
        self,
        course_id: uuid.UUID,
        progress: int
    ) -> None:
        async for session in get_async_session():
            update_query = (
                update(Course)
                .where(Course.id == course_id)
                .values(generation_progress=progress)
            )
            
            await session.execute(update_query)
            await session.commit()
            
    async def set_current_lesson(
        self,
        course_id: uuid.UUID,
        lesson_id: uuid.UUID
    ) -> None:
        async for session in get_async_session():
            update_query = (
                update(Course)
                .where(Course.id == course_id)
                .values(current_lesson_id=lesson_id)
            )
            
            await session.execute(update_query)
            await session.commit()
            
    async def set_course_completion(
        self,
        course_id: uuid.UUID
    ) -> None:
        async for session in get_async_session():
            update_query = (
                update(Course)
                .where(Course.id == course_id)
                .values(completed_at_utc=datetime.utcnow())
            )
            
            await session.execute(update_query)
            await session.commit()
            
    async def get_next_lesson(
        self,
        course_id: uuid.UUID,
        current_lesson_id: uuid.UUID
    ) -> Optional[Lesson]:
        async for session in get_async_session():
            course_query = (
                select(Course)
                .where(Course.id == course_id)
                .options(
                    joinedload(Course.modules)
                    .joinedload(Module.lessons)
                )
            )
            
            result = await session.execute(course_query)
            course = result.scalar_one_or_none()
            
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
            
    async def get_courses(self, user_id: uuid.UUID) -> list[Course]:
        async for session in get_async_session():
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
            
            result = await session.execute(query)
            courses = result.unique().scalars().all()
            
            return courses
        
    async def get_lesson_count(self, course_id: uuid.UUID) -> int:
        async for session in get_async_session():
            query = (
                select(Lesson.id)
                .join(Module, Lesson.module_id == Module.id)
                .where(Module.course_id == course_id)
            )
            
            result = await session.execute(query)
            lessons = result.scalars().all()
            
            return len(lessons)
        
    async def get_lesson(self, lesson_id: uuid.UUID) -> Optional[Lesson]:
        from sqlalchemy.orm import with_loader_criteria

        async for session in get_async_session():
            query = (
                select(Lesson)
                .where(Lesson.id == lesson_id)
                .options(
                    joinedload(Lesson.sections),
                    joinedload(Lesson.exercises)
                    .joinedload(CourseExercise.objectives),
                    with_loader_criteria(
                        CourseExercise, CourseExercise.is_unavailable == False
                    ),
                )
            )

            result = await session.execute(query)
            lesson = result.unique().scalar_one_or_none()

            return lesson
        
    async def get_course(self, course_id: uuid.UUID) -> Optional[Course]:
        """
        Retrieves a course by its ID, including related modules, lessons, sections, exercises, and objectives.

        Args:
            course_id (uuid.UUID): The ID of the course to retrieve.

        Returns:
            Optional[Course]: The course if found, None otherwise.
        """
        from sqlalchemy.orm import with_loader_criteria

        async for session in get_async_session():
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
                    with_loader_criteria(
                        CourseExercise, CourseExercise.is_unavailable == False
                    ),
                )
            )

            result = await session.execute(query)
            course = result.unique().scalar_one_or_none()

            if course is None:
                return None

            # Order by module, lesson, section "order" field
            course.modules.sort(key=lambda x: x.order)
            for module in course.modules:
                module.lessons.sort(key=lambda x: x.order)
                for lesson in module.lessons:
                    lesson.sections.sort(key=lambda x: x.order)

            return course
        
    async def get_exercise(
        self,
        exercise_id: uuid.UUID
    ) -> Optional[CourseExercise]:
        async for session in get_async_session():
            query = (
                select(CourseExercise)
                .where(CourseExercise.id == exercise_id)
                .options(
                    joinedload(CourseExercise.objectives)
                )
            )
            
            result = await session.execute(query)
            exercise = result.scalar_one_or_none()
            
            return exercise
        
    async def create_exercise(
        self,
        lesson_id: uuid.UUID, 
        environment_id: uuid.UUID, 
        title: str, 
        summary: str, 
        objectives: list[ExerciseObjectivePlan]
    ) -> uuid.UUID:
        async for session in get_async_session():
            exercise_entity = CourseExercise(
                lesson_id=lesson_id,
                title=title,
                environment_id=environment_id,
                summary=summary
            )
            
            session.add(exercise_entity)
            
            for objective in objectives:
                objective_entity = CourseExerciseObjective(
                    objective=objective.objective,
                    description=objective.description,
                    test_plan=objective.test_plan,
                    is_completed=False,
                    exercise_id=exercise_entity.id
                )
                
                session.add(objective_entity)
            
            await session.commit()
            await session.refresh(exercise_entity)
            
            return exercise_entity.id
        
    async def set_exercise_environment(self, exercise_id: uuid.UUID, environment_id: uuid.UUID) -> None:
        async for session in get_async_session():
            update_query = (
                update(CourseExercise)
                .where(CourseExercise.id == exercise_id)
                .values(environment_id=environment_id)
            )
            
            await session.execute(update_query)
            await session.commit()
            
    async def get_exercise_by_environment(self, environment_id: uuid.UUID) -> Optional[CourseExercise]:
        async for session in get_async_session():
            query = (
                select(CourseExercise)
                .where(CourseExercise.environment_id == environment_id)
                .options(
                    joinedload(CourseExercise.objectives)
                )
            )
            
            result = await session.execute(query)
            exercise = result.scalar_one_or_none()
            
            return exercise
            
    async def set_exercise_setup_error(self, exercise_id: uuid.UUID, detail: Optional[str] = None) -> None:
        """
        Removes an exercise and its objectives from the database

        Args:
            exercise_id (uuid.UUID): The ID of the exercise to remove
        """
        
        async for session in get_async_session():
            update_query = (
                update(CourseExercise)
                .where(CourseExercise.id == exercise_id)
                .values(is_unavailable=True, error_details=detail)
            )
            
            await session.execute(update_query)
            await session.commit()
            
    async def remove_exercise_setup_error(self, exercise_id: uuid.UUID) -> None:
        async for session in get_async_session():
            update_query = (
                update(CourseExercise)
                .where(CourseExercise.id == exercise_id)
                .values(is_unavailable=False, error_details=None)
            )
            
            await session.execute(update_query)
            await session.commit()
            
    async def set_objective_status(self, objective_id: uuid.UUID, is_complete: bool) -> None:
        async for session in get_async_session():
            update_query = (
                update(CourseExerciseObjective)
                .where(CourseExerciseObjective.id == objective_id)
                .values(is_completed=is_complete)
            )
            
            await session.execute(update_query)
            await session.commit()
    
    async def increment_exercise_build_attempts(self, exercise_id: uuid.UUID) -> None:
        async for session in get_async_session():
            update_query = (
                update(CourseExercise)
                .where(CourseExercise.id == exercise_id)
                .values(rebuild_attempts=CourseExercise.rebuild_attempts + 1)
            )
            
            await session.execute(update_query)
            await session.commit()