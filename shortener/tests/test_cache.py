from django.test import SimpleTestCase

from shortener.services.cache import RedisCacheService
from shortener.services.cache_keys import my_urls_cache_key


class RedisCacheServiceTests(SimpleTestCase):

    def setUp(self):
        self.cache = RedisCacheService()
        self.cache.client.flushdb()

    def tearDown(self):
        self.cache.client.flushdb()
        self.cache.delete("test:key")
        self.cache.delete("missing:key")
        self.cache.delete("exists:key")
        self.cache.delete("delete:key")

    def test_set_and_get(self):
        self.cache.set(
            "test:key",
            {"message": "hello"},
        )

        result = self.cache.get("test:key")

        self.assertEqual(
            result,
            {"message": "hello"},
        )

    def test_get_missing_key_returns_none(self):
        result = self.cache.get("missing:key")

        self.assertIsNone(result)

    def test_exists_returns_true_for_existing_key(self):
        self.cache.set(
            "exists:key",
            {"value": True},
        )

        self.assertTrue(self.cache.exists("exists:key"))

    def test_exists_returns_false_for_missing_key(self):
        self.assertFalse(self.cache.exists("missing:key"))

    def test_delete_removes_key(self):
        self.cache.set(
            "delete:key",
            {"value": "test"},
        )

        self.cache.delete("delete:key")

        self.assertIsNone(self.cache.get("delete:key"))


class CacheKeyTests(SimpleTestCase):

    def test_my_urls_cache_key_is_user_specific(self):
        user_1_key = my_urls_cache_key(1)
        user_2_key = my_urls_cache_key(2)

        self.assertTrue(user_1_key.startswith("user:1:my_urls:"))

        self.assertTrue(user_2_key.startswith("user:2:my_urls:"))

        self.assertNotEqual(
            user_1_key,
            user_2_key,
        )
