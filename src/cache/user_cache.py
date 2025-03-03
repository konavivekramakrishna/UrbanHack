import json

CACHE_EXPIRY = 86400  # 1 day in seconds

async def get_user_cache(redis_client, user_id: int):
    key = f"user:{user_id}"
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None

async def set_user_cache(redis_client, user_id: int, user_data: dict):
    key = f"user:{user_id}"
    await redis_client.set(key, json.dumps(user_data), ex=CACHE_EXPIRY)

async def invalidate_user_cache(redis_client, user_id: int):
    key = f"user:{user_id}"
    await redis_client.delete(key)
