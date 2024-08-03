from fastapi import Depends
from api.app.models.dto.user import UserOnboardingStatusDto
from api.app.repositories.user_repository import UserRepository


class UserOnboardingService:
    """
    Handles onboarding aspects of user management
    
    Attributes:
        user_repo (UserRepository): The repository for user data
    """    
    user_repo: UserRepository
    
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repo = user_repository
        
    async def get_onboarding_status(self, user_id: str) -> dict:
        """
        Retrieves the onboarding status for a user
        
        Args:
            user_id (str): The ID of the user to check
        
        Returns:
            dict: The user's onboarding status
        """
        user = await self.user_repo.get_user("id", user_id)
        
        # Check required profile fields
        is_profile_complete = all([
            user.profile.first_name,
            user.profile.last_name,
            user.profile.bio,
        ])
        
        return UserOnboardingStatusDto.model_construct(
            is_verified= not user.pending_verification,
            is_profile_complete=is_profile_complete
        )