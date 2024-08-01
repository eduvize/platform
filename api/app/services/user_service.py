import asyncio
import os
from typing import List
import uuid

from fastapi import Depends, UploadFile
from mimetypes import guess_extension, guess_type
from ..api.contracts.user_contracts import UpdateProfilePayload
from ..common.storage import StoragePurpose, get_bucket, get_public_object_url, object_exists
from ..models.schema.user import User, UserIdentifiers, UserIncludes, UserProfile
from ..repositories.user_repository import UserRepository

class UserCreationError(Exception):
    def __repr__(self):
        return "User creation failed"

class UserService:
    def __init__(self, user_repo: UserRepository = Depends(UserRepository)):
        self.user_repo = user_repo

    async def create_user(self, email_address: str, username: str, password_hash: str) -> User:
        existing_email, existing_username = await asyncio.gather(
            self.user_repo.get_user("email", email_address),
            self.user_repo.get_user("name", username)
        )
        
        if existing_email:
            raise UserCreationError("Email already in use")
        
        if existing_username:
            raise UserCreationError("Username already in use")
        
        # Create the user record
        user = await self.user_repo.create_user(email_address, username, password_hash)
        
        # Create a blank profile
        await self.user_repo.upsert_profile(user.id, UserProfile())
        
        return user
    
    async def get_user(self, by: UserIdentifiers, value: str, include: List[UserIncludes] = ["profile"]) -> User:
        user = await self.user_repo.get_user(by, value, include)
        
        if user is None:
            raise ValueError("User not found")
        
        return user
    
    async def update_profile(self, user_id: str, profile: UpdateProfilePayload):
        user = await self.get_user("id", user_id, ["profile"])
        
        if user is None:
            raise ValueError("User not found")
        
        if profile.avatar_file_id is not None:
            bucket = get_bucket(StoragePurpose.AVATAR)
            bucket_id = self._get_avatar_bucket_id(user_id, profile.avatar_file_id)
            
            if not object_exists(bucket, bucket_id):
                raise ValueError("Invalid file")
            
            avatar_url = get_public_object_url(StoragePurpose.AVATAR, bucket_id)
        else:
            avatar_url = user.profile.avatar_url
        
        await self.user_repo.upsert_profile(
            user.id, 
            UserProfile(
                first_name=profile.first_name,
                last_name=profile.last_name,
                bio=profile.bio,
                github_username=profile.github_username,
                avatar_url=avatar_url
            )
        )
        
    async def upload_avatar(self, user_id: str, file: UploadFile) -> str:
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
        
        return object_id
    
    def _get_avatar_bucket_id(self, user_id: str, object_id: str) -> str:
        return f"{user_id}/{object_id}"