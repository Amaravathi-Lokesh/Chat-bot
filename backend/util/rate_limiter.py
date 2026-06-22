import redis

redis_client = redis.Redis(
    host="host.docker.internal",
    port=6379,
    decode_responses=True
)

def check_rate_limit(
    user_id: int,
    limit: int = 30,
    window: int = 60
):
    key = f"rate_limit:{user_id}"

    current = redis_client.get(key)

    if current is None:
        redis_client.setex(
            key,
            window,
            1
        )
        return True

    if int(current) >= limit:
        return False

    redis_client.incr(key)

    return True