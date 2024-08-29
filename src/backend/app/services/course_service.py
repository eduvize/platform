import logging
from fastapi import Depends
from openai import OpenAI
from app.services import UserService
from app.repositories import CourseRepository
from app.utilities.profile import get_user_profile_text
from common.messaging.topics import Topic
from config import get_openai_key
from common.storage import StoragePurpose, import_from_url, get_public_object_url
from common.messaging import KafkaProducer
from domain.schema.courses.course import Course
from domain.dto.courses import CourseDto, CourseListingDto
from domain.dto.profile import UserProfileDto
from domain.dto.courses import CoursePlanDto
from domain.topics import CourseGenerationTopic
from ai.prompts import GetAdditionalInputsPrompt, GenerateCourseOutlinePrompt, GenerateModuleContentPrompt

class CourseService:
    user_service: UserService
    course_repo: CourseRepository
    openai: OpenAI
    kafka_producer: KafkaProducer
    
    def __init__(
        self,
        user_service: UserService = Depends(UserService),
        course_repo: CourseRepository = Depends(CourseRepository)
    ) -> None:
        self.user_service = user_service
        self.course_repo = course_repo
        self.openai = OpenAI(api_key=get_openai_key())
        self.kafka_producer = KafkaProducer()
    
    async def get_additional_inputs(
        self, 
        user_id: str,
        plan: CoursePlanDto
    ):
        """
        Comes up with additional questions to ask the user based on basic information provided

        Args:
            user_id (str): The ID of the user
            plan (CoursePlanDto): The course plan object

        Returns:
            AdditionalInputs: An object containing additional inputs to provide to the user through the frontend
        """
        
        user = await self.user_service.get_user("id", user_id, ["profile.*"])
        
        if user is None:
            raise ValueError("User not found")
        
        profile_dto = UserProfileDto.model_validate(user.profile)
        user_profile_text = get_user_profile_text(profile_dto)
        
        prompt = GetAdditionalInputsPrompt()
        
        return prompt.get_inputs(
            plan=plan,
            profile_text=user_profile_text
        )
        
    async def generate_course(
        self,
        user_id: str,
        plan: CoursePlanDto
    ) -> None:
        """
        Generates a course outline and cover image based on requirements. Submits a message
        to a Kafka topic to generate the course content in the background.

        Args:
            user_id (str): The ID of the user
            plan (CoursePlanDto): The course plan object
        """
        
        user = await self.user_service.get_user("id", user_id, ["profile.*"])
        
        if user is None:
            raise ValueError("User not found")
        
        profile_dto = UserProfileDto.model_validate(user.profile)
        user_profile_text = get_user_profile_text(profile_dto)
        
        # Generate a course outline based on user requirements and profile
        prompt = GenerateCourseOutlinePrompt()
        outline = prompt.get_outline(
            plan=plan,
            profile_text=user_profile_text
        )

        # Construct the course DTO        
        course_dto = CourseDto.model_construct(
            title=outline.course_title,
            description=outline.description,
            cover_image_url="",
            modules=[]
        )
        
        # Generate a cover image for the course
        cover_image_url = self.generate_cover_image(outline.course_subject)
        cover_image_obj_id = await import_from_url(cover_image_url, StoragePurpose.COURSE_ASSET)
        
        # Set the cover image URL to the public URL
        course_dto.cover_image_url = get_public_object_url(StoragePurpose.COURSE_ASSET, cover_image_obj_id)
        
        course_id = self.course_repo.create_course(
            user_id=user.id, 
            course_dto=course_dto
        )
        
        self.kafka_producer.produce_message(
            topic=Topic.GENERATE_NEW_COURSE,
            message=CourseGenerationTopic(
                course_id=course_id,
                course_outline=outline   
            ) 
        )
        
    async def get_courses(
        self,
        user_id: str
    ) -> list[CourseListingDto]:
        user = await self.user_service.get_user("id", user_id)
        
        if user is None:
            raise ValueError("User not found")
        
        return self.course_repo.get_courses(user.id)
        
    async def get_course(
        self,
        user_id: str,
        course_id: str
    ) -> Course:
        user = await self.user_service.get_user("id", user_id)
        
        if user is None:
            raise ValueError("User not found")
        
        course = self.course_repo.get_course(user.id, course_id)
        
        if course is None:
            raise ValueError("Course not found")
        
        return course

    def generate_cover_image(self, subject: str) -> str:
        response = self.openai.images.generate(
            model="dall-e-3",
            prompt=f"Icon of {subject}, dark background, cinema 4d, isomorphic",
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return response.data[0].url