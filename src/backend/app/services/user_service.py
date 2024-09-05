import asyncio
import os
from typing import List

from fastapi import Depends, UploadFile
from mimetypes import guess_extension, guess_type

from config import is_email_validation_enabled
from app.services.user_onboarding_service import UserOnboardingService
from domain.enums.auth import OAuthProvider
from domain.dto.profile import UserProfileDto
from common.storage import StoragePurpose, get_public_object_url, upload_object, import_from_url
from domain.schema.user import User, UserIdentifiers, UserIncludes
from app.utilities.string_generation import generate_random_string
from app.repositories import UserRepository

class UserCreationError(Exception):
    def __repr__(self):
        return "User creation failed"

class UserService:
    """
    Handles primary business logic associated with user accounts on the platform.
    
    Attributes:
        user_repo (UserRepository): The repository for user data
    """
    
    onboarding_service: UserOnboardingService
    user_repo: UserRepository
    is_email_validation_enabled: bool
    
    def __init__(self, user_onboarding_service: UserOnboardingService = Depends(UserOnboardingService), user_repo: UserRepository = Depends(UserRepository)):
        self.onboarding_service = user_onboarding_service
        self.user_repo = user_repo
        self.is_email_validation_enabled = is_email_validation_enabled()

    async def create_user(self, email_address: str, username: str, password_hash: str) -> User:
        """
        Creates a new user and profile

        Args:
            email_address (str): The user's email address
            username (str): The unique name for the user
            password_hash (str): A hash derived from the user's password

        Raises:
            UserCreationError: Email or username already in use

        Returns:
            User: The newly created user
        """
        existing_email, existing_username = await asyncio.gather(
            self.user_repo.get_user("email", email_address),
            self.user_repo.get_user("username", username)
        )
        
        if existing_email:
            raise UserCreationError("Email already in use")
        
        if existing_username:
            raise UserCreationError("Username already in use")
        
        # Create the user record
        user = await self.user_repo.create_user(
            email_address=email_address, 
            username=username, 
            password_hash=password_hash,
            set_email_validated=not self.is_email_validation_enabled
        )
        
        # Begin onboarding with verification
        if self.is_email_validation_enabled:
            await self.onboarding_service.send_verification_email(user.id)
        
        return user
    
    async def create_external_user(
        self,
        provider: OAuthProvider,
        user_id: str,
        email_address: str,
        avatar_url: str
    ) -> User:
        """
        Creates a new user with optional profile data from an external OAuth provider.

        Args:
            provider (OAuthProvider): The provider the user authenticated with
            user_id (str): The external user ID
            email_address (str): The user's email address
            avatar_url (str): The URL to the user's avatar

        Returns:
            User: The newly created user
        """
        
        existing_email = await self.user_repo.get_user("email", email_address)
        
        if existing_email:
            raise UserCreationError("Email already in use")
        
        username = f"{provider}_{generate_random_string(12)}"
        
        avatar_object_id = await import_from_url(avatar_url, StoragePurpose.AVATAR)
        avatar_url = get_public_object_url(StoragePurpose.AVATAR, avatar_object_id)
           
        user = await self.user_repo.create_user(
            email_address=email_address,
            username=username,
            password_hash=None,
            set_email_validated=True
        )
        
        await self.user_repo.create_external_auth(
            user_id=user.id,
            provider=provider.value,
            external_id=user_id
        )
        
        await self.user_repo.set_avatar_url(
            user_id=user.id,
            avatar_url=avatar_url
        )
        
        return user
    
    async def get_user(self, by: UserIdentifiers, value: str, include: List[UserIncludes] = ["profile.*"]) -> User:
        """
        Retrieves a user by one of their unique identifiers, optionally providing related data.
        Profiles are included by default.

        Args:
            by (UserIdentifiers): The type of identifier to search by
            value (str): The value of the identifier
            include (List[UserIncludes], optional): Which related entities to populate. Defaults to ["profile"].

        Raises:
            ValueError: User not found

        Returns:
            User: The user record
        """
        user = await self.user_repo.get_user(by, value, include)
        
        if user is None:
            raise ValueError("User not found")
        
        if user.external_auth:
            if user.external_auth.provider_id == OAuthProvider.GITHUB.value:
                user.username = user.external_auth.external_id
            
        return user
    
    async def update_profile(self, user_id: str, profile_dto: UserProfileDto):
        """
        Updates a user's profile with the provided data.

        Args:
            user_id (str): The ID of the user to update
            profile (UpdateProfilePayload): The new profile data

        Raises:
            ValueError: User not found
            ValueError: Invalid file was supplied for avatar
        """
        user = await self.get_user("id", user_id, include=[])
        
        if user is None:
            raise ValueError("User not found")
        
        if "hobby" not in profile_dto.learning_capacities:
            profile_dto.hobby = None
            
        if "student" not in profile_dto.learning_capacities:
            profile_dto.student = None
            
        if "professional" not in profile_dto.learning_capacities:
            profile_dto.professional = None

        await self.user_repo.upsert_profile(
            user_id=user.id, 
            profile=profile_dto
        )
        
    async def upload_avatar(self, user_id: str, file: UploadFile) -> str:
        """
        Handles the upload of an avatar file for a given user to supply during profile updates.

        Args:
            user_id (str): The ID of the user to upload the avatar for
            file (UploadFile): The file to upload

        Raises:
            ValueError: User not found

        Returns:
            str: The object ID of the uploaded file in the storage bucket
        """
        user = await self.get_user("id", user_id)
        
        if user is None:
            raise ValueError("User not found")
        
        # Parse out mimetype and extension
        mimetype, _ = guess_type(file.filename)
        extension = os.path.splitext(file.filename)[1] if not mimetype else guess_extension(mimetype)
        
        # Upload it
        object_id = await upload_object(StoragePurpose.AVATAR, file.file, extension)
        
        public_url = get_public_object_url(StoragePurpose.AVATAR, object_id)
        
        await self.user_repo.set_avatar_url(
            user_id=user_id, 
            avatar_url=public_url
        )