from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from config import get_basic_auth_username, get_basic_auth_password

policy = HTTPBasic()

def basic_authorization(credentials: HTTPBasicCredentials = Depends(policy)) -> bool:
    """
    Validates the provided basic authorization credentials

    Args:
        credentials (HTTPBasicCredentials): The basic authorization credentials provided in the request

    Returns:
        bool: True if the credentials are valid, False otherwise
    """
    return credentials.username == get_basic_auth_username() and credentials.password == get_basic_auth_password()