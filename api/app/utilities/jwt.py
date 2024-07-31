
from datetime import datetime, timedelta
from typing import Optional

import jwt

def create_token(data: dict, secret: str, expiration_minutes: int) -> str:
    data_copy = data.copy()
    expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        
    data_copy.update({"exp": expiration})
    token = jwt.encode(data_copy, secret, algorithm="HS256")
    
    return token

def decode_token(token: str, secret: Optional[str]) -> dict:
    try:
        data = jwt.decode(token, secret, algorithms=["HS256"])
        return data
    except jwt.PyJWTError:
        raise ValueError("Invalid token received")