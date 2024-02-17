from datetime import datetime, timedelta
from collections import defaultdict

WINDOWS = defaultdict(list)

def sliding_window_logs_rate_limited(identifier, window_size=60, window_requests_threshold=60):
    if identifier in WINDOWS:
        first_request_time = WINDOWS[identifier][0]
        if datetime.now() - first_request_time < timedelta(seconds=window_size):
            if len(WINDOWS[identifier]) >= window_requests_threshold:
                return True
        else:
            del WINDOWS[identifier]
    WINDOWS[identifier].append(datetime.now())
    return False
