import asyncio
import functools
import os
import time

from loguru import logger

from app.extensions.db_extras import get_mongo_db
from app.extensions.redis_extras import RedisPool


def retry_on_exceptions(exceptions, max_retries=3, interval=1):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except tuple(exceptions) as e:
                    logger.info(f"Caught exception: {type(e).__name__}")
                    retries += 1
                    if retries < max_retries:
                        logger.info(f"Retrying in {interval} seconds...")
                        await asyncio.sleep(interval)
                    else:
                        logger.warning("Max retries exceeded. Giving up.")
                        raise e

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except tuple(exceptions) as e:
                    logger.info(f"Caught exception: {type(e).__name__}")
                    retries += 1
                    if retries < max_retries:
                        logger.info(f"Retrying in {interval} seconds...")
                        time.sleep(interval)
                    else:
                        logger.warning("Max retries exceeded. Giving up.")
                        raise e

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


def process_locker(lock_key, lock_ttl=60):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with RedisPool() as redis:
                os.getpid()
                lock_success = await redis.incr(lock_key, 1)
                if lock_success == 1:
                    await redis.expire(lock_key, lock_ttl)
                    logger.info(f"锁定成功，key：{lock_key}")
                else:
                    logger.warning(f"锁定失败，key：{lock_key}")
                    return
                # 执行原始函数
                try:
                    result = await func(*args, **kwargs)
                finally:
                    # 可以在这里做一些后处理的事情
                    await redis.delete(lock_key)
                    logger.info(f"解锁成功，key：{lock_key}")

            return result

        return wrapper

    return decorator


def init_mongo_db(db_name="flight_fare"):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            from motor.motor_asyncio import AsyncIOMotorClient
            from pymongo.server_api import ServerApi

            # Set the Stable API version when creating a new client
            mongo_db = await get_mongo_db(db_name)
            if 'mongo_db' not in kwargs:
                kwargs['mongo_db'] = mongo_db
            return await func(*args, **kwargs)

        return wrapper

    return decorator
