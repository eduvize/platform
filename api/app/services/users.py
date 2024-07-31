from typing import Union

from app.models.schema.user import User
from ..repositories.users import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, email_address: str, username: str, password_hash: str) -> User:
        user = self.user_repo.create_user(email_address, username, password_hash)
        return user

    def get_user_by_email(self, email: str) -> User:
        user = self.user_repo.get_user("email", email, include=["profile"])
            
        if user is None:
            raise ValueError("User not found")
        
        return user
    
    def get_user_by_name(self, name: str) -> User:
        user = self.user_repo.get_user("name", name, include=["profile"])
        
        if user is None:
            raise ValueError("User not found")
        
        return user