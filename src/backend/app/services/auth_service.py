from fastapi import Depends
from passlib.context import CryptContext
from config import get_token_expiration, get_token_secret
from ..services.user_service import UserService
from ..utilities.jwt import create_token

class AuthService:
    """
    Handles all authentication and authorization logic for the application

    Attributes:
        user_service (UserService): The service for interacting with user data
        crypto_context (CryptContext): The context for password hashing and verification
    """
    user_service: UserService
    crypto_context: CryptContext
    
    def __init__(self, user_service: UserService = Depends(UserService)):
        self.user_service = user_service
        
        # Set up a bcrypt provider for password hashing
        self.crypto_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async def authenticate(
        self, 
        email: str, 
        password: str
    ) -> str:
        """
        Handles authenticating a user and generating an access token

        Args:
            email (str): The user's email address
            password (str): The user's password

        Raises:
            ValueError: Invalid password

        Returns:
            str: The generated access token
        """
        user = await self.user_service.get_user("email", email)
        
        if not self._verify_password(password, user.password_hash):
            raise ValueError("Invalid password")
        
        return self._generate_token(str(user.id))
    
    async def register(
        self, 
        email: str, 
        username: str, 
        password: str
    ) -> str:
        """
        Handles the registration of a new user and generating an access token after successful registration

        Args:
            email (str): The email address of the user
            username (str): The unique name of the user
            password (str): The password of the user

        Returns:
            str: The generated access token
        """
        hashed_password = self._get_password_hash(password)
        
        user = await self.user_service.create_user(email, username, hashed_password)
        
        return self._generate_token(str(user.id))
    
    def _generate_token(
        self, 
        user_id: str
    ) -> str:
        """
        Generates a new user access token using configuration values for signing key and expiration

        Args:
            user_id (str): The user's unique identifier

        Returns:
            str: The generated access token
        """
        signing_key = get_token_secret()
        token_expiration_minutes = get_token_expiration()
        
        return create_token({"id": user_id}, signing_key, token_expiration_minutes)
    
    def _verify_password(
        self, 
        plain: str, 
        hashed: str
    ) -> bool:
        """
        Verifies a provided password against the correct hash

        Args:
            plain (str): The plain text password
            hashed (str): The hashed password to compare against

        Returns:
            bool: Whether the password is correct
        """
        return self.crypto_context.verify(plain, hashed)
    
    def _get_password_hash(
        self, 
        password: str
    ) -> str:
        """
        Generates a cryptographic hash of a password using the configured hashing algorithm (bcrypt)

        Args:
            password (str): The plaintext password to hash

        Returns:
            str: A hashed version of the password
        """
        return self.crypto_context.hash(password)