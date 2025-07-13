#!/usr/bin/env python3
"""
Module for Redis basic operations.
"""
import redis
import uuid
from typing import Union, Callable

class Cache:
    """
    Cache class for storing data in Redis.
    """
    def __init__(self):
        """
        Initialize the Cache instance.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random key.

        Args:
            data (Union[str, bytes, int, float]): The data to store.

        Returns:
            str: The generated random key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it using a callable.

        Args:
            key (str): The key to retrieve.
            fn (Callable, optional): A callable to convert the data.

        Returns:
            Union[str, bytes, int, float, None]: The retrieved data, optionally converted.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        """
        Retrieve a string from Redis.

        Args:
            key (str): The key to retrieve.

        Returns:
            Union[str, None]: The retrieved string.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Union[int, None]:
        """
        Retrieve an integer from Redis.

        Args:
            key (str): The key to retrieve.

        Returns:
            Union[int, None]: The retrieved integer.
        """
        return self.get(key, fn=int)

def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function.

    Args:
        method (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """
    def wrapper(*args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store input arguments
        self = args[0]  # Extract the instance
        self._redis.rpush(input_key, str(args[1:]))

        # Execute the original method
        output = method(*args, **kwargs)

        # Store output
        self._redis.rpush(output_key, str(output))

        return output

    return wrapper

# Decorate Cache.store with call_history
Cache.store = call_history(Cache.store)