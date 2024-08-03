from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from ...utilities.endpoints import get_public_endpoint, get_public_ui_endpoint

def redirect_ui(endpoint: str):
    """
    Returns a redirect response to the client to navigate to a relative endpoint based on the environment configuration

    Args:
        endpoint (str): The relative endpoint to redirect to
    """
    
    public_ui_endpoint = get_public_ui_endpoint(endpoint)
    
    return RedirectResponse(public_ui_endpoint)

def redirect(endpoint: str):
    """
    Returns a redirect response to the client to navigate to a relative endpoint based on the environment configuration

    Args:
        endpoint (str): The relative endpoint to redirect to
    """
    
    public_endpoint = get_public_endpoint(endpoint)
    
    return RedirectResponse(public_endpoint)

def raise_unauthorized():
    """
    Returns an unauthorized response to the client

    Raises:
        HTTPException: 401 - Unauthorized
    """
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    
def raise_bad_request(detail: str):
    """
    Returns a bad request response to the client with a given detail message

    Args:
        detail (str): The detail message to include in the response

    Raises:
        HTTPException: 400 - Bad Request
    """
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )