from flask import request
from enum import Enum

from token_bucket import token_bucket_rate_limited
from sliding_window_logs import sliding_window_logs_rate_limited
from fixed_window_counter import fixed_window_counter_rate_limited
from sliding_window_counter import sliding_window_counter_rate_limited

class RateLimiter(Enum):
    TOKEN_BUCKET = token_bucket_rate_limited
    FIXED_WINDOW_COUNTER = fixed_window_counter_rate_limited
    SLIDING_WINDOW_LOGS = sliding_window_logs_rate_limited
    SLIDING_WINDOW_COUNTER = sliding_window_counter_rate_limited

def rate_limiter(type: RateLimiter, **fargs):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ip_address = request.remote_addr
            fargs.update({
                'identifier': ip_address
            })
            rate_limited = type
            if rate_limited(**fargs):
                return 'You have been rate limited!', 429
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator
