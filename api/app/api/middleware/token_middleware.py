from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from app.utilities.jwt import decode_token
from config import get_token_secret

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def token_extractor(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return decode_token(token, get_token_secret())
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token received"
        )
    
def user_id_extractor(token: dict = Depends(token_extractor)) -> str:
    return token.get("id")