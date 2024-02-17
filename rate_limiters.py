from collections import defaultdict
from flask import request
from datetime import datetime, timedelta
import time

# In real world scenario this bucket will be in a distributed cache
BUCKET = dict()
def refill_bucket(ip_address, capacity, refill_ts):
    current_ts = int(time.time())
    if ip_address not in BUCKET:
        BUCKET[ip_address] = {
            'size': capacity,
            'last_ts': current_ts
        }
    bucket = BUCKET[ip_address]
    ts = current_ts - bucket['last_ts']
    bucket['size'] += (ts//refill_ts)
    bucket['size'] = min(bucket['size'], capacity)
    bucket['last_ts'] = current_ts
    BUCKET[ip_address].update(bucket)
    
def token_bucket_rate_limit(capacity=10, refill_ts=1):
    """Utilizing token bucket algorithm for rate limiting
    Each bucket is identifed by the ip address of the requester
    Args:
        capacity (int, optional): size of a bucket. Defaults to 10.
        refill_ts (int, optional): refill a bucket time interval. Defaults to 1.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            ip_address = request.remote_addr
            refill_bucket(ip_address, capacity, refill_ts)
            if BUCKET[ip_address]['size'] > 0:
                BUCKET[ip_address]['size']-=1
                return func(*args, **kwargs)
            else:
                return 'You have been rate limited!', 429
        return wrapper
    return decorator

WINDOWS = {}
def sliding_window_log_rate_limit(size=60, threshold=60):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ip_address = request.remote_addr
            def rate_limit_exceeded(ip_address, size, threshold):
                if ip_address in WINDOWS:
                    first_request_time = WINDOWS[ip_address][0]
                    if datetime.now() - first_request_time < timedelta(seconds=size):
                        if len(WINDOWS[ip_address]) >= threshold:
                            return True
                    else:
                        del WINDOWS[ip_address]
                return False
            if rate_limit_exceeded(ip_address, size, threshold):
                return 'You have been rate limited!', 429
            else:
                if ip_address in WINDOWS:
                    WINDOWS[ip_address].append(datetime.now())
                else:
                    WINDOWS[ip_address] = [datetime.now()]
            return func(*args, **kwargs)
        return wrapper
    return decorator


FIXED_WINDOW_COUNTER = defaultdict(int)
def fixed_window_counter_rate_limit(size=60, threshold=60):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ip_address = request.remote_addr
            def rate_limit_exceeded(ip_address, size, threshold):
                current_ts = int(time.time())
                current_window = current_ts//size
                key = f'{ip_address}:{current_window}'
                if FIXED_WINDOW_COUNTER[key] >= threshold:
                    return True
                FIXED_WINDOW_COUNTER[key] += 1
            if rate_limit_exceeded(ip_address, size, threshold):
                return 'You have been rate limited!', 429
            return func(*args, **kwargs)
        return wrapper
    return decorator
