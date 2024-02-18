import time
from collections import defaultdict

FIXED_WINDOW_COUNTER = defaultdict(int)

def fixed_window_counter_rate_limited(identifier, window_size=60, window_requests_threshold=5, redis_client=None):
    current_ts = int(time.time())
    current_window = current_ts//window_size
    key = f'{identifier}:{current_window}'
    if redis_client:
        redis_val = redis_client.get(key)
        curr_requests = int(redis_val.decode()) if redis_val else 0
    else:
        curr_requests = FIXED_WINDOW_COUNTER[key]
    if curr_requests >= window_requests_threshold:
        return True
    if redis_client:
        redis_client.incr(key)
    else:
        FIXED_WINDOW_COUNTER[key] += 1
    return False
