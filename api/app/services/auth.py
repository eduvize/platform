from fastapi import Depends
from passlib.context import CryptContext
from app.services.users import UserService
from app.utilities.jwt import create_token
from config import get_token_expiration, get_token_secret

class AuthService:
    user_service: UserService
    crypto_context: CryptContext
    
    def __init__(self, user_service: UserService = Depends(UserService)):
        self.user_service = user_service
        self.crypto_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async def authenticate(self, email: str, password: str) -> str:
        user = await self.user_service.get_user("email", email)
        
        if not self._verify_password(password, user.password_hash):
            raise ValueError("Invalid password")
        
        return self._generate_token(str(user.id))
    
    async def register(self, email: str, username: str, password: str) -> str:
        hashed_password = self._get_password_hash(password)
        
        user = await self.user_service.create_user(email, username, hashed_password)
        
        return self._generate_token(str(user.id))
    
    def _generate_token(self, user_id: str) -> str:
        signing_key = get_token_secret()
        token_expiration_minutes = get_token_expiration()
        
        return create_token({"id": user_id}, signing_key, token_expiration_minutes)
    
    def _verify_password(self, plain: str, hashed: str):
        return self.crypto_context.verify(plain, hashed)
    
    def _get_password_hash(self, password: str) -> str:
        return self.crypto_context.hash(password)