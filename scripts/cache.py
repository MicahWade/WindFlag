"""
Caching utility for the WindFlag CTF platform using Redis.
Provides functions and a decorator for easy caching of data.
"""
import json
from flask import current_app
from functools import wraps

def _get_redis_client():
    """Helper to get the Redis client from the current app context."""
    if current_app and hasattr(current_app, 'redis') and current_app.redis:
        return current_app.redis
    return None

def cache_key(prefix, *args, **kwargs):
    """
    Generates a consistent cache key based on a prefix and function arguments.
    Converts args and kwargs to a sorted, stable string representation.
    """
    args_str = "_".join(map(str, args))
    kwargs_str = "_".join(f"{k}-{v}" for k, v in sorted(kwargs.items()))
    
    # Simple hash for very long keys to prevent Redis key limits, though less readable
    # For now, a direct concatenation should be fine.
    return f"{prefix}:{args_str}:{kwargs_str}".replace(' ', '_').replace('.', '_').replace(':', '_').replace('-', '_')

def get_from_cache(key):
    """
    Retrieves data from Redis cache.
    Expects JSON-serialized data.
    """
    redis_client = _get_redis_client()
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        current_app.logger.error(f"Error retrieving from Redis for key {key}: {e}")
    return None

def set_to_cache(key, value, timeout=300):
    """
    Stores data in Redis cache.
    Serializes data to JSON.
    """
    redis_client = _get_redis_client()
    if not redis_client:
        return
    try:
        redis_client.setex(key, timeout, json.dumps(value))
    except Exception as e:
        current_app.logger.error(f"Error setting to Redis for key {key}: {e}")

def invalidate_cache(key_pattern):
    """
    Deletes keys matching a pattern from Redis cache.
    Use with caution as KEYS can be a blocking operation on large datasets.
    Consider using SCAN in production for large caches.
    """
    redis_client = _get_redis_client()
    if not redis_client:
        return
    try:
        # For simplicity, using KEYS. In a very large production system,
        # consider using SCAN with a generator to avoid blocking.
        keys = redis_client.keys(key_pattern)
        if keys:
            redis_client.delete(*keys)
            current_app.logger.info(f"Invalidated {len(keys)} keys matching pattern: {key_pattern}")
    except Exception as e:
        current_app.logger.error(f"Error invalidating cache for pattern {key_pattern}: {e}")

def cached(key_prefix, timeout=300):
    """
    Decorator to cache function results in Redis.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # If current_app is not available (e.g., during app factory setup)
            # or caching is disabled, just run the function
            if not _get_redis_client():
                return f(*args, **kwargs)

            # Generate cache key
            key = cache_key(key_prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = get_from_cache(key)
            if cached_result is not None:
                current_app.logger.debug(f"Cache hit for key: {key}")
                return cached_result
            
            current_app.logger.debug(f"Cache miss for key: {key}")
            # If not in cache, call original function
            result = f(*args, **kwargs)
            
            # Store result in cache
            set_to_cache(key, result, timeout)
            return result
        return decorated_function
    return decorator
