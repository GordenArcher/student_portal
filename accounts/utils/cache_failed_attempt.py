from django.core.cache import cache


def cache_failed_attempt(ip_address):
    """Cache failed login attempts with expiration"""
    cache_key = f'failed_login_attempts_{ip_address}'
    current_attempts = cache.get(cache_key)
    if current_attempts is None:
        current_attempts = 0
    current_attempts += 1
    cache.set(cache_key, current_attempts, 900)  # 15 minutes expiration
    return current_attempts