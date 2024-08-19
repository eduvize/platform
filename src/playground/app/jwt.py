from datetime import datetime, timedelta
import jwt

def create_token(
    data: dict, 
    secret: str, 
    expiration_minutes: int
) -> str:
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