from datetime import datetime, timedelta

WINDOWS = dict()

def rate_limit_exceeded(identifier, size, threshold):
    if identifier in WINDOWS:
        first_request_time = WINDOWS[identifier][0]
        if datetime.now() - first_request_time < timedelta(seconds=size):
            if len(WINDOWS[identifier]) >= threshold:
                return True
        else:
            del WINDOWS[identifier]
    return False

def sliding_window_logs_rate_limited(identifier, window_size=60, window_requests_threshold=60):
    if rate_limit_exceeded(identifier, window_size, window_requests_threshold):
        return 'You have been rate limited!', 429
    else:
        if identifier in WINDOWS:
            WINDOWS[identifier].append(datetime.now())
        else:
            WINDOWS[identifier] = [datetime.now()]
