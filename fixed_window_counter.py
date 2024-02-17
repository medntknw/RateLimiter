import time
from collections import defaultdict

FIXED_WINDOW_COUNTER = defaultdict(int)

def fixed_window_counter_rate_limited(identifier, window_size=60, window_requests_threshold=60):
    current_ts = int(time.time())
    current_window = current_ts//window_size
    key = f'{identifier}:{current_window}'
    if FIXED_WINDOW_COUNTER[key] >= window_requests_threshold:
        return True
    FIXED_WINDOW_COUNTER[key] += 1
    return False
