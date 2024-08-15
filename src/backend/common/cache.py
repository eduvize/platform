from typing import List, Optional, Union
import redis
from config import get_redis_host

redis_host = get_redis_host()
if ":" in redis_host:
    host, port = redis_host.split(":")
    port = int(port)
else:
    host = redis_host
    port = 6379
    
def _get_client():
    return redis.Redis(host=host, port=port)

def set_key(
    key: str, 
    value: str, 
    expiration: int = None
):
    """
    Sets a key in the Redis cache

    Args:
        key (str): The key to set
        value (str): The value to set
        expiration (int): The expiration time in seconds
    """
    
    client = _get_client()
    
    client.set(key, value, ex=expiration)
    
def get_key(key: str) -> Optional[str]:
    """
    Gets a key from the Redis cache

    Args:
        key (str): The key to get

    Returns:
        str: The value of the key
    """
    
    client = _get_client()
    
    return client.get(key)

def add_to_set(
    key: str, 
    value: Union[str, List[str]]
):
    """
    Adds a value to a set in the Redis cache

    Args:
        key (str): The key of the set
        value (str): The value to add
    """
    
    client = _get_client()
    
    if isinstance(value, list):
        for v in value:
            client.sadd(key, v)
    else:
        client.sadd(key, value)
    
def remove_from_set(
    key: str, 
    value: Union[str, List[str]]
):
    """
    Removes a value from a set in the Redis cache

    Args:
        key (str): The key of the set
        value (str): The value to remove
    """
    
    client = _get_client()
    
    if isinstance(value, list):
        for v in value:
            client.srem(key, v)
    else:
        client.srem(key, value)
    
def get_set(key: str) -> List[str]:
    """
    Gets all values in a set from the Redis cache

    Args:
        key (str): The key of the set

    Returns:
        List[str]: The values in the set
    """
    
    client = _get_client()
    
    return client.smembers(key)