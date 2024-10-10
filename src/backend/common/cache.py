from typing import List, Optional, Union
from config import get_redis_host
from time import time
import aioredis

async def _get_client():
    redis_host = get_redis_host()
    if ":" in redis_host:
        host, port = redis_host.split(":")
        port = int(port)
    else:
        host = redis_host
        port = 6379
        
    return await aioredis.create_redis_pool(f"redis://{host}:{port}")

async def set_key(
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
    
    client = await _get_client()
    
    if expiration:
        await client.setex(key, expiration, value)
    else:
        await client.set(key, value)
    
    client.close()
    await client.wait_closed()
        
async def delete_key(key: str):
    """
    Deletes a key from the Redis cache

    Args:
        key (str): The key to delete
    """
    
    client = await _get_client()
    
    await client.delete(key)
    
    client.close()
    await client.wait_closed()
    
async def get_key(key: str) -> Optional[str]:
    """
    Gets a key from the Redis cache

    Args:
        key (str): The key to get

    Returns:
        str: The value of the key
    """
    
    client = await _get_client()
    value = await client.get(key)
    
    client.close()
    await client.wait_closed()
    
    return value.decode('utf-8') if value else None

async def add_to_set(
    key: str, 
    value: Union[str, List[str]]
):
    """
    Adds a value to a set in the Redis cache

    Args:
        key (str): The key of the set
        value (str): The value to add
    """
    
    client = await _get_client()
    
    if isinstance(value, list):
        for v in value:
            await client.sadd(key, v)
    else:
        await client.sadd(key, value)
    
    client.close()
    await client.wait_closed()
        
async def add_to_set_with_expiration(
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
    
    client = await _get_client()
    
    if isinstance(value, list):
        for v in value:
            await client.zadd(key, int(time() + expiration), v)
    else:
        await client.zadd(key, int(time() + expiration), value)
    
    client.close()
    await client.wait_closed()
    
async def remove_from_set(
    key: str, 
    value: Union[str, List[str]]
):
    """
    Removes a value from a set in the Redis cache

    Args:
        key (str): The key of the set
        value (str): The value to remove
    """
    
    client = await _get_client()
    
    if isinstance(value, list):
        for v in value:
            await client.srem(key, v)
    else:
        await client.srem(key, value)
    
    client.close()
    await client.wait_closed()
        
async def remove_from_set_with_expiration(
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
    
    client = await _get_client()
    
    if isinstance(value, list):
        for v in value:
            await client.zrem(key, v)
    else:
        await client.zrem(key, value)
    
    client.close()
    await client.wait_closed()
        
async def is_in_set(
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
    
    client = await _get_client()
    
    result = await client.sismember(key, value)
    
    client.close()
    await client.wait_closed()
    
    return result

async def is_in_set_with_expiration(
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
    
    client = await _get_client()
    
    await client.zremrangebyscore(key, 0, int(time()))
    
    result = await client.zrank(key, value) is not None
    
    client.close()
    await client.wait_closed()
    
    return result
    
async def get_set(key: str) -> List[str]:
    """
    Gets all values in a set from the Redis cache

    Args:
        key (str): The key of the set

    Returns:
        List[str]: The values in the set
    """
    
    client = await _get_client()
    
    result = await client.smembers(key)
    
    client.close()
    await client.wait_closed()
    
    return result

async def get_set_with_expiration(key: str) -> List[str]:
    """
    Gets all values in a sorted set from the Redis cache with an expiration time.
    This method removes expired values from the set before returning valid values.

    Args:
        key (str): The key of the set

    Returns:
        List[str]: The values in the set
    """
    
    client = await _get_client()
    
    await client.zremrangebyscore(key, 0, int(time()))
    
    result = await client.zrange(key, 0, -1)
    
    client.close()
    await client.wait_closed()
    
    return result