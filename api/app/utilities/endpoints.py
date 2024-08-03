from config import get_public_ui_url, get_public_url

def get_public_ui_endpoint(path: str) -> str:
    """
    Gets a publicly accessible endpoint for a given path based on environment configuration

    Args:
        path (str): The path to generate the endpoint for

    Returns:
        str: The full URL for the endpoint
    """
    
    public_ui_url = get_public_ui_url()
    
    return f"{public_ui_url}/{path}"

def get_public_endpoint(path: str) -> str:
    """
    Gets a publicly accessible endpoint for a given path based on environment configuration

    Args:
        path (str): The path to generate the endpoint for

    Returns:
        str: The full URL for the endpoint
    """
    
    public_url_base = get_public_url()
    
    return f"{public_url_base}/{path}"