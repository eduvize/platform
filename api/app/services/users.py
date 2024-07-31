from typing import Union
from ..models.dto.user import UserDto
from ..repositories.users import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_user(self, identifier: Union[str, int]) -> UserDto:
        if isinstance(identifier, int):
            user = self.user_repo.get_user_by_id(identifier, include=["profile"])
        else:
            user = self.user_repo.get_user_by_name(identifier, include=["profile"])
            
        if user is None:
            raise ValueError("User not found")
        
        return UserDto.model_validate(user)