import asyncio
import os
from typing import List
import uuid

from fastapi import Depends, UploadFile
from mimetypes import guess_extension, guess_type

from app.services.user_onboarding_service import UserOnboardingService
from domain.dto.profile import UserProfileDto
from common.storage import StoragePurpose, get_bucket, get_public_object_url
from domain.schema.user import User, UserIdentifiers, UserIncludes
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
    
    def __init__(self, user_onboarding_service: UserOnboardingService = Depends(UserOnboardingService), user_repo: UserRepository = Depends(UserRepository)):
        self.onboarding_service = user_onboarding_service
        self.user_repo = user_repo

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
        user = await self.user_repo.create_user(email_address, username, password_hash)
        
        # Begin onboarding with verification
        await self.onboarding_service.send_verification_email(user.id)
        
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
        
        # Get the S3 bucket
        bucket = get_bucket(StoragePurpose.AVATAR)
        
        # Parse out mimetype and extension
        mimetype, _ = guess_type(file.filename)
        extension = os.path.splitext(file.filename)[1] if not mimetype else guess_extension(mimetype)
        
        # Create the object and bucket IDs
        object_id = uuid.uuid4().hex + extension
        bucket_id = self._get_avatar_bucket_id(user_id, object_id)
        
        # Upload the file
        bucket.put_object(Key=bucket_id, Body=await file.read(), ContentType=mimetype, ACL="public-read")
        
        await self.user_repo.set_avatar_url(user_id, get_public_object_url(StoragePurpose.AVATAR, bucket_id))
    
    def _get_avatar_bucket_id(self, user_id: str, object_id: str) -> str:
        """
        Helper function to generate the avatar bucket ID for a specific user

        Args:
            user_id (str): The user ID
            object_id (str): The object ID

        Returns:
            str: A bucket ID
        """
        return f"{user_id}/{object_id}"