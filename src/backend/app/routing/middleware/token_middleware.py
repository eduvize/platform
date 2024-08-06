from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from config import get_token_secret
from app.routing.responses import raise_unauthorized
from app.utilities.jwt import InvalidJWTToken, decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def token_extractor(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extracts the JWT information from the request token

    Args:
        token (str, optional): The token provided in an HTTP request.

    Raises:
        HTTPException: 401 - Invalid token received

    Returns:
        dict: The decoded token information
    """
    try:
        return decode_token(token, get_token_secret())
    except InvalidJWTToken:
        raise_unauthorized()
    
def user_id_extractor(token: dict = Depends(token_extractor)) -> str:
    """
    Extracts the authorized user's ID from the token in the request

    Args:
        token (dict, optional): The decoded token information from the request

    Returns:
        str: The user's ID
    """
    return token.get("id")