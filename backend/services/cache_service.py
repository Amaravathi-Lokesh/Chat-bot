import redis
import json

redis_client = redis.Redis(
    host="redis-server",
    port=6379,
    decode_responses=True
)

class CacheService:

    @staticmethod
    def get(key):

        value = redis_client.get(key)

        if value:
            return json.loads(value)

        return None

    @staticmethod
    def set(
        key,
        value,
        ttl=3600
    ):

        redis_client.setex(
            key,
            ttl,
            json.dumps(value)
        )