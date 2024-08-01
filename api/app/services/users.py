import asyncio
from typing import Union

from fastapi import Depends

from app.models.schema.user import User, UserProfile
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
    
    async def get_user_by_id(self, user_id: Union[str, int]) -> User:
        user = await self.user_repo.get_user("id", user_id, include=["profile"])
        
        if user is None:
            raise ValueError("User not found")
        
        return user

    async def get_user_by_email(self, email: str) -> User:
        user = await self.user_repo.get_user("email", email, include=["profile"])
            
        if user is None:
            raise ValueError("User not found")
        
        return user
    
    async def get_user_by_name(self, name: str) -> User:
        user = await self.user_repo.get_user("name", name, include=["profile"])
        
        if user is None:
            raise ValueError("User not found")
        
        return user