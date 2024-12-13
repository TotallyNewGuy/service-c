import os
import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.exceptions import ConnectionError
from redis.backoff import ExponentialBackoff
from redis.exceptions import BusyLoadingError

_redis_client = None

async def init_redis() -> None:
    redis_url = os.environ.get("REDIS_URL")
    try:
        global _redis_client
        if _redis_client is None:
            retry = Retry(ExponentialBackoff(), retries=5)
            _redis_client = redis.from_url(redis_url, retry=retry, retry_on_error=[ConnectionError, BusyLoadingError, TimeoutError], db=0, decode_responses=True)

        await _redis_client.ping()

    except Exception as e:
        raise Exception(f"initialize Redis failed due to: {str(e)}")


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()


def get_redis_client():
    return _redis_client


if __name__ == "__main__":
    import asyncio
    async def main():
        await init_redis()

    asyncio.run(main())