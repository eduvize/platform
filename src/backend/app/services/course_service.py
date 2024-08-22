import json
import logging
from fastapi import Depends
from app.services import UserService
from app.repositories import CourseRepository
from app.utilities.profile import get_user_profile_text
from domain.dto.courses import CourseDto
from domain.dto.profile import UserProfileDto
from domain.dto.courses import CoursePlanDto
from ai.prompts import GetAdditionalInputsPrompt, GenerateCourseOutlinePrompt, GenerateModuleContentPrompt

class CourseService:
    user_service: UserService
    course_repo: CourseRepository
    
    def __init__(
        self,
        user_service: UserService = Depends(UserService),
        course_repo: CourseRepository = Depends(CourseRepository)
    ) -> None:
        self.user_service = user_service
        self.course_repo = course_repo
    
    async def get_additional_inputs(
        self, 
        user_id: str,
        plan: CoursePlanDto
    ):
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
    ):
        user = await self.user_service.get_user("id", user_id, ["profile.*"])
        
        if user is None:
            raise ValueError("User not found")
        
        profile_dto = UserProfileDto.model_validate(user.profile)
        user_profile_text = get_user_profile_text(profile_dto)
        
        prompt = GenerateCourseOutlinePrompt()
        
        outline = prompt.get_outline(
            plan=plan,
            profile_text=user_profile_text
        )
        
        logging.info(outline.model_dump_json(indent=4))
        
        course_dto = CourseDto.model_construct(
            title=outline.course_title,
            description=outline.long_description,
            modules=[]
        )
        
        for module in outline.modules:
            module_prompt = GenerateModuleContentPrompt()
            module_dto = module_prompt.generate_module_content(
                course=outline,
                module=module
            )
            
            logging.info(f"Generated module '{module_dto.title}'")
            
            course_dto.modules.append(module_dto)
            
        self.course_repo.create_course(
            user_id=user.id, 
            course_dto=course_dto
        )
        