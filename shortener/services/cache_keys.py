import hashlib


def my_urls_cache_key(user_id, query_string=""):
    query_hash = hashlib.sha256(query_string.encode()).hexdigest()[:16]

    return f"user:{user_id}:my_urls:{query_hash}"


def my_urls_cache_pattern(user_id):
    return f"user:{user_id}:my_urls:*"
