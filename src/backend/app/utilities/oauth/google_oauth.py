import requests

from config import get_google_client_id, get_google_client_secret, get_auth_redirect_url
from domain.dto.oauth import GoogleUser


def exchange_code_for_token(code: str) -> str:
    """
    Exchanges a GitHub OAuth code for an access token

    Args:
        code (str): The OAuth code to exchange for an access token

    Returns:
        str: The access token
    """
    
    client_id = get_google_client_id()
    client_secret = get_google_client_secret()
    redirect_url = get_auth_redirect_url()
    
    response = requests.post(
        f"https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_url,
            "grant_type": "authorization_code"
        }
    )
    
    response.raise_for_status()
    
    return response.json()["access_token"]

def get_user_info(access_token: str) -> GoogleUser:
    """
    Gets the user ID from a GitHub access token

    Args:
        access_token (str): The GitHub access token

    Returns:
        GoogleUser: The Google user object
    """
    
    response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    response.raise_for_status()
    
    data = response.json()
    
    return GoogleUser(
        name=data["name"],
        username=data["sub"],
        email_address=data["email"],
        avatar_url=data["picture"]
    )