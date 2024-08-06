import datetime
from fastapi import Depends

from app.utilities.endpoints import get_public_endpoint
from app.common.email import send_email
from domain.dto.user import UserOnboardingStatusDto
from app.repositories.user_repository import UserRepository
from app.common.email.templates import get_welcome_email
from app.utilities.string_generation import generate_random_string

class VerificationExpiredError(Exception):
    """
    Error raised when a verification code has expired
    """
    def __repr__(self):
        return "Verification code has expired"

class UserOnboardingService:
    """
    Handles onboarding aspects of user management
    
    Attributes:
        user_repo (UserRepository): The repository for user data
    """    
    user_repo: UserRepository
    
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repo = user_repository
        
    async def send_verification_email(self, user_id: str) -> None:
        """
        Sends a verification email to a user
        
        Args:
            user_id (str): The ID of the user to send the email to
        """
        user = await self.user_repo.get_user("id", user_id)
        
        # Generate a code and construct the email
        verification_code = generate_random_string(12)
        email_body = get_welcome_email(
            username=user.username,
            verification_link=get_verification_url(verification_code)
        )
        send_email(user.email, "Wecome to Eduvize", email_body)
        
        # Reset verification code information in the database
        await self.user_repo.set_verification_code(user_id, verification_code)
        
    async def verify_user(self, code: str):
        """
        Verifies a user based on a verification code
        
        Args:
            code (str): The verification code to check
        """
        user = await self.user_repo.get_user("verification_code", code)
        
        if user is None:
            raise ValueError("Invalid verification code")
        
        if user.verification_sent_at_utc is None or datetime.datetime.utcnow() - user.verification_sent_at_utc > datetime.timedelta(hours=1):
            raise VerificationExpiredError()
        
        await self.user_repo.mark_verified(user.id)
        
    async def get_onboarding_status(self, user_id: str) -> UserOnboardingStatusDto:
        """
        Retrieves the onboarding status for a user
        
        Args:
            user_id (str): The ID of the user to check
        
        Returns:
            dict: The user's onboarding status
        """
        user = await self.user_repo.get_user("id", user_id, ["profile"])
        
        # Check required profile fields
        is_profile_complete = all([
            user.profile.first_name,
            user.profile.last_name,
            user.profile.bio,
        ])
        
        return UserOnboardingStatusDto.model_construct(
            is_verified= not user.pending_verification,
            is_profile_complete=is_profile_complete,
            recently_verified=(
                not user.pending_verification
                and user.verification_sent_at_utc is not None 
                and datetime.datetime.utcnow() - user.verification_sent_at_utc < datetime.timedelta(seconds=10)
            )
        )
        
def get_verification_url(code: str) -> str:
    """
    Generates a verification URL for a given code
    
    Args:
        code (str): The verification code to use
        
    Returns:
        str: The verification URL
    """
    return get_public_endpoint(f"onboarding/verify?code={code}")