from collections import defaultdict
import time

SLIDING_WINDOW_COUNTER = defaultdict(int)

def sliding_window_counter_rate_limited(identifier, window_size=60, window_requests_threshold=5):
    current_ts = time.time()
    print(f'Current ts: {current_ts}')
    current_window = current_ts//window_size
    previous_window = current_window - 1
    curr_window_key = f'{identifier}:{current_window}'
    prev_window_key = f'{identifier}:{previous_window}'
    prev_window_count = SLIDING_WINDOW_COUNTER[prev_window_key]
    curr_window_count = SLIDING_WINDOW_COUNTER[curr_window_key]
    print(f'Prev window count: {prev_window_count}\n Curr window count: {curr_window_count}')
    if curr_window_count >= window_requests_threshold:
        return True
    time_elapsed_in_curr_window = current_ts % window_size
    print(f'time elapsed: {time_elapsed_in_curr_window}')
    percentage_elapsed = time_elapsed_in_curr_window / window_size
    print(f'Percentage elapsed: {percentage_elapsed}')
    current_request_rate = curr_window_count + prev_window_count * (1 - percentage_elapsed)
    print(f'current request rate: {current_request_rate}')
    if current_request_rate >= window_requests_threshold:
        return True
    SLIDING_WINDOW_COUNTER[curr_window_key] += 1
    return False
