from flask import request
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
