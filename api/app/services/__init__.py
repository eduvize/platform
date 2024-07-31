from fastapi import Depends
from ..repositories import get_user_repository
from ..repositories.users import UserRepository
from .users import UserService

def get_user_service(user_repository: UserRepository = Depends(get_user_repository)):
    return UserService(user_repository)