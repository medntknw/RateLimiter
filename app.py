from flask import Flask
from rate_limiters import RateLimiter
from rate_limiters import rate_limiter
import redis


app = Flask(__name__)

redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.route('/limited')
@rate_limiter(RateLimiter.FIXED_WINDOW_COUNTER, redis_client=redis_client)
def limited():
    return "Limited, don't over use me!"

@app.route('/unlimited')
def unlimited():
    return "Unlimited! Let's Go!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
