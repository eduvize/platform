import asyncio
from typing import Union

from fastapi import Depends

from app.models.dto.user import UserProfileDto
from app.models.schema.user import User, UserIdentifiers, UserProfile
from ..repositories.users import UserRepository

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
    
    async def get_user(self, by: UserIdentifiers, value: str) -> User:
        user = await self.user_repo.get_user(by, value, include=["profile"])
        
        if user is None:
            raise ValueError("User not found")
        
        return user
    
    async def update_profile(self, user_id: str, profile: UserProfileDto):
        user = await self.get_user("id", user_id)
        
        if user is None:
            raise ValueError("User not found")
        
        await self.user_repo.upsert_profile(
            user.id, 
            UserProfile(
                first_name=profile.first_name,
                last_name=profile.last_name,
                bio=profile.bio,
                github_username=profile.github_username
            )
        )