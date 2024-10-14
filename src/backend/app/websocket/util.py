import logging
from typing import Optional

from socketio import AsyncNamespace


def get_token_from_environ(environ: dict) -> Optional[str]:
    """
    Extracts the token from the header information associated with the connect event.

    Args:
        environ (dict): The environment data from the websocket connection.

    Returns:
        Optional[str]: The token if it exists, as a UTF-8 string.
    """
    scope = environ.get("asgi.scope")
    
    if not scope:
        return None
    
    headers = scope.get("headers")
    
    if not headers:
        return None
    
    for header in headers:
        key, value = header
        if key.decode("utf-8").lower() == "authorization":
            try:
                token = value.decode("utf-8")
                if token.startswith("Bearer "):
                    return token[len("Bearer "):].strip()
                else:
                    logging.warning(f"Authorization header does not start with 'Bearer ': {token}")
                    return None
            except UnicodeDecodeError as e:
                logging.error(f"Failed to decode token: {e}")
                return None
    
    return None