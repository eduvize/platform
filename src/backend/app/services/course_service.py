from fastapi import Depends
from app.services import UserService
from app.utilities.profile import get_user_profile_text
from domain.dto.profile import UserProfileDto
from domain.dto.courses import CoursePlanDto
from ai.prompts import GetAdditionalInputsPrompt

class CourseService:
    user_service: UserService
    
    def __init__(
        self,
        user_service: UserService = Depends(UserService)    
    ) -> None:
        self.user_service = user_service
    
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