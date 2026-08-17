import json

import redis
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder


class RedisCacheService:

    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=int(settings.REDIS_PORT),
            decode_responses=True,
        )

    def set(self, key, value, timeout=300):
        self.client.setex(
            key,
            timeout,
            json.dumps(
                value,
                cls=DjangoJSONEncoder,
            ),
        )

    def get(self, key):
        value = self.client.get(key)

        if value is None:
            return None

        return json.loads(value)

    def delete(self, key):
        self.client.delete(key)

    def exists(self, key):
        return bool(self.client.exists(key))

    def delete_pattern(self, pattern):
        keys = self.client.scan_iter(match=pattern)

        for key in keys:
            self.client.delete(key)
