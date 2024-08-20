import datetime
from fastapi import Depends

from app.utilities.endpoints import get_public_endpoint
from common.email import send_email
from domain.dto.user import UserOnboardingStatusDto
from app.repositories.user_repository import UserRepository
from common.email.templates import get_welcome_email
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
    
    def __init__(
        self, 
        user_repository: UserRepository = Depends(UserRepository)
    ):
        self.user_repo = user_repository
        
    async def send_verification_email(
        self, 
        user_id: str
    ) -> None:
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
            self.send_verification_email(user.id)
            
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
        is_profile_complete = await self.is_profile_complete(user_id)
        
        return UserOnboardingStatusDto.model_construct(
            is_verified= not user.pending_verification,
            is_profile_complete=is_profile_complete,
            recently_verified=(
                not user.pending_verification
                and user.verification_sent_at_utc is not None 
                and datetime.datetime.utcnow() - user.verification_sent_at_utc < datetime.timedelta(seconds=10)
            )
        )
        
    async def is_profile_complete(self, user_id: str) -> bool:
        user = await self.user_repo.get_user(
            by="id", 
            value=user_id, 
            include=["profile.*"]
        )
        
        if user is None:
            return False
        
        if user.profile is None:
            return False
        
        profile = user.profile
        
        if (
            profile.first_name is None or profile.first_name.strip() == "" or
            profile.last_name is None or profile.last_name.strip() == "" or
            profile.bio is None or profile.bio.strip() == "" or
            profile.disciplines is None
            or len(profile.disciplines) == 0
            or len(profile.skills) == 0
        ):
            return False
        
        if profile.hobby is None and profile.student is None and profile.professional is None:
            return False
        
        if profile.hobby:
            if profile.hobby.reasons is None or len(profile.hobby.reasons) == 0:
                return False
            
            if any([
                project.project_name is None
                or project.project_name.strip() == ""
                or project.description is None
                or project.description.strip() == ""
                for project in profile.hobby.projects
            ]):
                return False
            
        if profile.student:
            if(
                profile.student.schools is None 
                or len(profile.student.schools) == 0
                or len(profile.student.schools) == 0
            ):
                return False
            
            if any([(
                    school.school_name is None
                    or school.school_name.strip() == "" 
                    or school.focus is None
                    or school.focus.strip() == ""
                    or school.start_date is None
                    or (school.end_date is None and not school.is_current)
                    or school.did_finish is None
                    or len(school.skills) == 0
                )
                for school in profile.student.schools
            ]):
                return False
            
        if profile.professional:
            if profile.professional.employers is None or len(profile.professional.employers) == 0:
                return False
            
            if any([
                employer.company_name is None or
                employer.company_name.strip() == "" or
                employer.position is None or
                employer.position.strip() == "" or
                employer.start_date is None or
                (employer.end_date is None and not employer.is_current) or
                employer.description is None
                or employer.description.strip() == ""
                for employer in profile.professional.employers
            ]):
                return False
            
        return True
        
def get_verification_url(code: str) -> str:
    """
    Generates a verification URL for a given code
    
    Args:
        code (str): The verification code to use
        
    Returns:
        str: The verification URL
    """
    return get_public_endpoint(f"onboarding/verify?code={code}")