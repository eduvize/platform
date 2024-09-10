import redis
from datetime import timedelta
from typing import List, Optional, Union
from config import get_redis_host
from time import time

    
def _get_client():
    redis_host = get_redis_host()
    if ":" in redis_host:
        host, port = redis_host.split(":")
        port = int(port)
    else:
        host = redis_host
        port = 6379
        
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
    
    if expiration:
        expiration_delta = timedelta(seconds=expiration)
        client.setex(key, expiration_delta, value)
    else:
        client.set(key, value)
        
def delete_key(key: str):
    """
    Deletes a key from the Redis cache

    Args:
        key (str): The key to delete
    """
    
    client = _get_client()
    
    client.delete(key)
    
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
        
def add_to_set_with_expiration(
    key: str, 
    value: Union[str, List[str]], 
    expiration: int
):
    """
    Adds a value to a sorted set in the Redis cache with an expiration time.
    When reading the set, expired values will not be returned and will be removed.
    
    Args:
        key (str): The key of the set
        value (str): The value to add
        expiration (int): The expiration time in seconds
    """
    
    client = _get_client()
    
    if isinstance(value, list):
        for v in value:
            client.zadd(key, {v: int(time() + expiration)})
    else:
        client.zadd(key, {value: int(time() + expiration)})
    
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
        
def remove_from_set_with_expiration(
    key: str, 
    value: Union[str, List[str]]
):
    """
    Removes a value from a sorted set in the Redis cache with an expiration time.
    When reading the set, expired values will not be returned and will be removed.
    
    Args:
        key (str): The key of the set
        value (str): The value to remove
    """
    
    client = _get_client()
    
    if isinstance(value, list):
        for v in value:
            client.zrem(key, v)
    else:
        client.zrem(key, value)
        
def is_in_set(
    key: str, 
    value: str
) -> bool:
    """
    Checks if a value is in a set in the Redis cache

    Args:
        key (str): The key of the set
        value (str): The value to check

    Returns:
        bool: True if the value is in the set, False otherwise
    """
    
    client = _get_client()
    
    return client.sismember(key, value)

def is_in_set_with_expiration(
    key: str, 
    value: str
) -> bool:
    """
    Checks if a value is in a sorted set in the Redis cache with an expiration time.
    This method removes expired values from the set before checking for the value.

    Args:
        key (str): The key of the set
        value (str): The value to check

    Returns:
        bool: True if the value is in the set, False otherwise
    """
    
    client = _get_client()
    
    client.zremrangebyscore(key, 0, int(time()))
    
    return client.zrank(key, value) is not None
    
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

def get_set_with_expiration(key: str) -> List[str]:
    """
    Gets all values in a sorted set from the Redis cache with an expiration time.
    This method removes expired values from the set before returning valid values.

    Args:
        key (str): The key of the set

    Returns:
        List[str]: The values in the set
    """
    
    client = _get_client()
    
    client.zremrangebyscore(key, 0, int(time()))
    
    return client.zrange(key, 0, -1)