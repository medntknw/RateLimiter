from flask import Flask
from rate_limiters import RateLimiter
from rate_limiters import rate_limiter

app = Flask(__name__)

@app.route('/limited')
@rate_limiter(RateLimiter.TOKEN_BUCKET)
def limited():
    return "Limited, don't over use me!"

@app.route('/unlimited')
def unlimited():
    return "Unlimited! Let's Go!"

if __name__ == '__main__':
    app.run(debug=True)
