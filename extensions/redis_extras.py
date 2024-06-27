import aioredis

from app import settings


async def get_redis_pool():
    async with RedisPool() as redis:
        yield redis


class RedisPool:
    def __init__(self, redis_url=settings.REDIS_URL, **kwargs):
        self.redis_pool = None
        self.redis_url = redis_url
        self.ext_options = kwargs
        if 'decode_responses' not in self.ext_options:
            self.ext_options['decode_responses'] = True

    async def __aenter__(self):
        self.redis_pool = await aioredis.from_url(self.redis_url, **self.ext_options)
        return self.redis_pool

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.redis_pool.close()
        if exc_type is not None:
            raise exc_val
