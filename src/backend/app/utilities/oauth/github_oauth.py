from typing import List
from pydantic import BaseModel
import requests
from config import get_github_client_id, get_github_client_secret
from domain.dto.oauth import GitHubUser

class GitHubEmail(BaseModel):
    email: str
    primary: bool
    verified: bool

def exchange_code_for_token(code: str) -> str:
    """
    Exchanges a GitHub OAuth code for an access token

    Args:
        code (str): The OAuth code to exchange for an access token

    Returns:
        str: The access token
    """
    
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={
            "Accept": "application/json"
        },
        data={
            "client_id": get_github_client_id(),
            "client_secret": get_github_client_secret(),
            "code": code
        }
    )
    
    response.raise_for_status()
    
    return response.json()["access_token"]
        
def get_user_info(access_token: str) -> GitHubUser:
    """
    Gets the user ID from a GitHub access token

    Args:
        access_token (str): The GitHub access token

    Returns:
        str: The user ID
    """
    
    response = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    response.raise_for_status()
    
    data = response.json()
    
    if not data["email"]:
        email_addresses = get_email_addresses(access_token)
        primary = next((email for email in email_addresses if email.primary), None)
        
        data["email"] = primary.email if primary else None
    
    return GitHubUser(
        name=data["name"],
        username=data["login"],
        email_address=data["email"],
        avatar_url=data["avatar_url"],
        bio=data["bio"]
    )
    
def get_email_addresses(access_token: str) -> List[GitHubEmail]:
    """
    Gets the email addresses associated with a GitHub account

    Args:
        access_token (str): The GitHub access token

    Returns:
        List[str]: The email addresses associated with the account
    """
    
    response = requests.get(
        "https://api.github.com/user/emails",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    response.raise_for_status()
    
    data =  response.json()
    
    return [
        GitHubEmail(
            email=email["email"],
            primary=email["primary"],
            verified=email["verified"]
        )
        for email in data
    ]