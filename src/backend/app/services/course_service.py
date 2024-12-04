import logging
from typing import Optional
import uuid
from fastapi import Depends
from openai import AsyncOpenAI as OpenAI

from domain.dto.courses.exercise_plan import ExercisePlan
from .user_service import UserService
from app.repositories import CourseRepository
from common.messaging.topics import Topic
from config import get_openai_key
from common.storage import StoragePurpose, import_from_url, get_public_object_url
from common.messaging import KafkaProducer
from domain.schema.courses import Course, Lesson, CourseExercise
from domain.dto.courses import CourseListingDto, CourseProgressionDto
from domain.topics import CourseCreatedTopic
from ai.prompts import GenerateExercisesPrompt

class CourseService:
    user_service: UserService
    course_repo: CourseRepository
    openai: OpenAI
    
    def __init__(
        self,
        user_service: UserService = Depends(UserService),
        course_repo: CourseRepository = Depends(CourseRepository)
    ) -> None:
        self.user_service = user_service
        self.course_repo = course_repo
        self.openai = OpenAI(api_key=get_openai_key())
        
    async def generate_course(
        self,
        user_id: str,
        course_title: str,
        course_summary: str,
        key_outcomes: list[str],
        topics: list[str]
    ) -> None:
        """
        Generates a course outline and cover image based on requirements. Submits a message
        to a Kafka topic to generate the course content in the background.

        Args:
            user_id (str): The ID of the user
            course_title (str): The title of the course
            course_summary (str): A summary of the course
            key_outcomes (list[str]): The key outcomes of the course
            topics (list[str]): The topics of the course
        """
        
        user = await self.user_service.get_user("id", user_id)
        
        if user is None:
            raise ValueError("User not found")
        
        # Generate a cover image for the course
        cover_image_url = await self.generate_cover_image(f"{course_title} {course_summary}")
        cover_image_obj_id = await import_from_url(cover_image_url, StoragePurpose.COURSE_ASSET)
        
        course_id = await self.course_repo.create_course(
            user_id=user.id, 
            course_title=course_title,
            course_description=course_summary,
            cover_image_url=get_public_object_url(StoragePurpose.COURSE_ASSET, cover_image_obj_id)
        )
        
        async with KafkaProducer() as kafka_producer:
            await kafka_producer.produce_message(
                topic=Topic.COURSE_CREATED,
                message=CourseCreatedTopic(
                    user_id=uuid.UUID(user_id),
                    course_id=course_id,
                    course_title=course_title,
                    course_description=course_summary,
                    key_outcomes=key_outcomes,
                    topics=topics
                )
            )
            
    async def get_lesson(
        self,
        lesson_id: uuid.UUID
    ) -> Lesson:
        return await self.course_repo.get_lesson(lesson_id)
        
    async def mark_lesson_complete(
        self,
        user_id: uuid.UUID,
        course_id: uuid.UUID,
        lesson_id: uuid.UUID
    ) -> CourseProgressionDto:
        user = await self.user_service.get_user("id", user_id)
        
        if user is None:
            raise ValueError("User not found")
        
        course = await self.course_repo.get_course(course_id)
        
        if course is None:
            raise ValueError("Course not found")
        
        current_lesson: Optional[Lesson] = next((
            lesson
            for module in course.modules
            for lesson in module.lessons
            if lesson.id == course.current_lesson_id
        ), None)
        
        if current_lesson is None:
            print(course)
            raise ValueError("Current lesson not found")
        
        # Don't do anything if it's not the current lesson
        if current_lesson.id != lesson_id:
            return CourseProgressionDto.model_construct(
                is_course_complete=False,
                lesson_id=current_lesson.id
            )
            
        if len(current_lesson.exercises) > 0:
            # They need to fully complete the exercises before moving on
            if not all(objective.is_completed for objective in current_lesson.exercises[0].objectives):
                return CourseProgressionDto.model_construct(
                    is_course_complete=False,
                    lesson_id=current_lesson.id
                )
                
        next_lesson = await self.course_repo.get_next_lesson(
            course_id=course.id,
            current_lesson_id=course.current_lesson_id
        )
        
        if next_lesson is None:
            # They're finished with the course
            next_lesson_id = None
        else:
            # Move to section #1 of the next lesson
            next_lesson_id = next_lesson.id
        
        if next_lesson_id:
            await self.course_repo.set_current_lesson(
                course_id=course.id,
                lesson_id=next_lesson_id,
            )
        else:
            await self.course_repo.set_course_completion(course.id)
            
        return CourseProgressionDto.model_construct(
            is_course_complete=next_lesson_id is None,
            lesson_id=next_lesson_id,
        )
        
    async def mark_lesson_section_complete(
        self,
        user_id: uuid.UUID,
        course_id: uuid.UUID,
        lesson_id: uuid.UUID,
        section_index: int
    ) -> CourseProgressionDto:
        user = await self.user_service.get_user("id", user_id)
        
        if user is None:
            raise ValueError("User not found")
        
        course = await self.course_repo.get_course(course_id)
        
        if course is None:
            raise ValueError("Course not found")
        
        current_lesson: Optional[Lesson] = next((
            lesson
            for module in course.modules
            for lesson in module.lessons
            if lesson.id == course.current_lesson_id
        ), None)
        
        if current_lesson is None:
            raise ValueError("Current lesson not found")
        
        if current_lesson.id != lesson_id:
            return CourseProgressionDto.model_construct(
                is_course_complete=False,
                lesson_id=current_lesson.id
            )
        
        if section_index < course.current_section_index:
            return CourseProgressionDto.model_construct(
                is_course_complete=False,
                lesson_id=current_lesson.id
            )
        
        if len(current_lesson.sections) > section_index + 1:
            await self.course_repo.set_current_section(
                course_id=course.id,
                lesson_id=lesson_id,
                section_index=section_index + 1
            )
        
        return CourseProgressionDto.model_construct(
            is_course_complete=False,
            lesson_id=current_lesson.id
        )
        
    async def get_courses(
        self,
        user_id: str
    ) -> list[CourseListingDto]:
        user = await self.user_service.get_user("id", user_id)
        
        if user is None:
            raise ValueError("User not found")
        
        courses = await self.course_repo.get_courses(user.id)
        
        async def calculate_progress(course: Course) -> int:
            total_lessons = await self.course_repo.get_lesson_count(course.id)
            current_lesson = next((
                lesson
                for module in course.modules
                for lesson in module.lessons
                if lesson.id == course.current_lesson_id
            ), None)
            
            if current_lesson is None:
                return 0
            
            return int((current_lesson.order / total_lessons) * 100)
        
        return [
            CourseListingDto.model_construct(
                id=course.id,
                title=course.title,
                description=course.description,
                cover_image_url=course.cover_image_url,
                progress=await calculate_progress(course),
                is_generating=course.is_generating,
                generation_progress=course.generation_progress
            )
            for course in courses
        ]
        
    async def get_course(
        self,
        user_id: str,
        course_id: str
    ) -> Course:
        user = await self.user_service.get_user("id", user_id)
        
        if user is None:
            raise ValueError("User not found")
        
        course = await self.course_repo.get_course(course_id)
        
        if course is None:
            raise ValueError("Course not found")
        
        return course
    
    async def get_exercise(
        self,
        exercise_id: uuid.UUID
    ) -> CourseExercise:
        exercise = await self.course_repo.get_exercise(exercise_id)
        
        if exercise is None:
            raise ValueError("Exercise not found")
        
        return exercise
    
    async def set_objective_status(
        self,
        exercise_id: uuid.UUID,
        objective_id: uuid.UUID,
        is_complete: bool
    ) -> None:
        await self.course_repo.set_objective_status(objective_id, is_complete)

    async def generate_cover_image(self, subject: str) -> str:
        response = await self.openai.images.generate(
            model="dall-e-3",
            prompt=f"Icon of {subject}, dark background, cinema 4d, isomorphic",
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return response.data[0].url
    
    async def get_exercises(self, course_id: uuid.UUID) -> Optional[list[ExercisePlan]]:
        course = await self.course_repo.get_course(course_id)
        
        if course is None:
            raise ValueError("Course not found")
        
        exercises: list[ExercisePlan] = []
        
        for module in course.modules:
            logging.info(f"Generating exercises for module: {module.title}")
            
            for lesson in module.lessons:
                logging.info(f"Generating exercises for lesson: {lesson.title}")
                
                lesson_content = "\n".join([
                    section.content
                    for section in lesson.sections
                ])
                
                prompt = GenerateExercisesPrompt()
                lesson_exercise = prompt.get_exercise(lesson_content)
                
                if lesson_exercise is not None:
                    exercises.append(lesson_exercise)
                    
        return exercises