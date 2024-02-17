import time

BUCKETS = {}

class Bucket:
    def __init__(self, size, last_update_ts):
        self.size = size
        self.last_update_ts = last_update_ts

def refill_bucket(identifier, bucket_max_sz, refill_interval, refill_amount=1):
    current_ts = time.time()
    if identifier not in BUCKETS:
        BUCKETS[identifier] = Bucket(bucket_max_sz, current_ts)
    bucket = BUCKETS[identifier]
    time_elapsed_till_last_update = current_ts - bucket.last_update_ts
    refill_count = (time_elapsed_till_last_update//refill_interval)
    bucket.size = min(bucket_max_sz, bucket.size + refill_count * refill_amount)
    bucket.last_update_ts = min(current_ts, bucket.last_update_ts + refill_count * refill_interval)
    BUCKETS[identifier] = bucket

def token_bucket_rate_limited(identifier, bucket_max_sz=10, refill_interval=60, refill_amount=1):
    refill_bucket(identifier, bucket_max_sz, refill_interval, refill_amount)
    if BUCKETS[identifier].size > 0:
        BUCKETS[identifier].size -= 1
        return False
    else:
        return True
