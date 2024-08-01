
from datetime import datetime, timedelta
from typing import Optional

import jwt

def create_token(data: dict, secret: str, expiration_minutes: int) -> str:
    """
    Creates a new JWT token using the provided data, signing key, and expiration time

    Args:
        data (dict): The data to encode into the token
        secret (str): The secret key to use for signing the token
        expiration_minutes (int): The number of minutes until the token expires

    Returns:
        str: The generated JWT token
    """
    data_copy = data.copy()
    expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        
    data_copy.update({"exp": expiration})
    token = jwt.encode(data_copy, secret, algorithm="HS256")
    
    return token

def decode_token(token: str, secret: Optional[str]) -> dict:
    """
    Validates and decodes a JWT token using the provided secret key

    Args:
        token (str): The token to decode
        secret (Optional[str]): The secret key to use for decoding the token

    Raises:
        ValueError: Invalid token received

    Returns:
        dict: The decoded token data
    """
    try:
        data = jwt.decode(token, secret, algorithms=["HS256"])
        return data
    except jwt.PyJWTError:
        raise ValueError("Invalid token received")