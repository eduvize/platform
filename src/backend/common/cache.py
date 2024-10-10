import redis.asyncio as redis
from datetime import timedelta
from typing import List, Optional, Union
from config import get_redis_host
from time import time


async def _get_client() -> redis.Redis:
    """
    Initializes and returns an asynchronous Redis client.

    Returns:
        redis.Redis: The Redis client instance.
    """
    redis_host = get_redis_host()
    if ":" in redis_host:
        host, port = redis_host.split(":")
        port = int(port)
    else:
        host = redis_host
        port = 6379

    return redis.Redis(host=host, port=port, decode_responses=True)


async def set_key(
    key: str,
    value: str,
    expiration: Optional[int] = None
) -> None:
    """
    Sets a key in the Redis cache.

    Args:
        key (str): The key to set.
        value (str): The value to set.
        expiration (Optional[int]): The expiration time in seconds.
    """
    client = await _get_client()

    if expiration:
        await client.setex(key, timedelta(seconds=expiration), value)
    else:
        await client.set(key, value)


async def delete_key(key: str) -> None:
    """
    Deletes a key from the Redis cache.

    Args:
        key (str): The key to delete.
    """
    client = await _get_client()
    await client.delete(key)


async def get_key(key: str) -> Optional[str]:
    """
    Gets a key from the Redis cache.

    Args:
        key (str): The key to get.

    Returns:
        Optional[str]: The value of the key, or None if not found.
    """
    client = await _get_client()
    return await client.get(key)


async def add_to_set(
    key: str,
    value: Union[str, List[str]]
) -> None:
    """
    Adds a value to a set in the Redis cache.

    Args:
        key (str): The key of the set.
        value (Union[str, List[str]]): The value or list of values to add.
    """
    client = await _get_client()

    if isinstance(value, list):
        await client.sadd(key, *value)
    else:
        await client.sadd(key, value)


async def add_to_set_with_expiration(
    key: str,
    value: Union[str, List[str]],
    expiration: int
) -> None:
    """
    Adds a value to a sorted set in the Redis cache with an expiration time.
    When reading the set, expired values will not be returned and will be removed.

    Args:
        key (str): The key of the set.
        value (Union[str, List[str]]): The value or list of values to add.
        expiration (int): The expiration time in seconds.
    """
    client = await _get_client()
    current_time = int(time()) + expiration

    if isinstance(value, list):
        mapping = {v: current_time for v in value}
        await client.zadd(key, mapping)
    else:
        await client.zadd(key, {value: current_time})


async def remove_from_set(
    key: str,
    value: Union[str, List[str]]
) -> None:
    """
    Removes a value from a set in the Redis cache.

    Args:
        key (str): The key of the set.
        value (Union[str, List[str]]): The value or list of values to remove.
    """
    client = await _get_client()

    if isinstance(value, list):
        await client.srem(key, *value)
    else:
        await client.srem(key, value)


async def remove_from_set_with_expiration(
    key: str,
    value: Union[str, List[str]]
) -> None:
    """
    Removes a value from a sorted set in the Redis cache with an expiration time.
    When reading the set, expired values will not be returned and will be removed.

    Args:
        key (str): The key of the set.
        value (Union[str, List[str]]): The value or list of values to remove.
    """
    client = await _get_client()

    if isinstance(value, list):
        await client.zrem(key, *value)
    else:
        await client.zrem(key, value)


async def is_in_set(
    key: str,
    value: str
) -> bool:
    """
    Checks if a value is in a set in the Redis cache.

    Args:
        key (str): The key of the set.
        value (str): The value to check.

    Returns:
        bool: True if the value is in the set, False otherwise.
    """
    client = await _get_client()
    return await client.sismember(key, value)


async def is_in_set_with_expiration(
    key: str,
    value: str
) -> bool:
    """
    Checks if a value is in a sorted set in the Redis cache with an expiration time.
    This method removes expired values from the set before checking for the value.

    Args:
        key (str): The key of the set.
        value (str): The value to check.

    Returns:
        bool: True if the value is in the set, False otherwise.
    """
    client = await _get_client()
    await client.zremrangebyscore(key, 0, int(time()))
    rank = await client.zrank(key, value)
    return rank is not None


async def get_set(key: str) -> List[str]:
    """
    Gets all values in a set from the Redis cache.

    Args:
        key (str): The key of the set.

    Returns:
        List[str]: The values in the set.
    """
    client = await _get_client()
    members = await client.smembers(key)
    return list(members)


async def get_set_with_expiration(key: str) -> List[str]:
    """
    Gets all values in a sorted set from the Redis cache with an expiration time.
    This method removes expired values from the set before returning valid values.

    Args:
        key (str): The key of the set.

    Returns:
        List[str]: The values in the set.
    """
    client = await _get_client()
    await client.zremrangebyscore(key, 0, int(time()))
    return await client.zrange(key, 0, -1)