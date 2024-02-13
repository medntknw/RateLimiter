from flask import Flask
from rate_limiters import token_bucket_rate_limit

app = Flask(__name__)

@app.route('/limited')
@token_bucket_rate_limit()
def limited():
    return "Limited, don't over use me!"

@app.route('/unlimited')
def unlimited():
    return "Unlimited! Let's Go!"

if __name__ == '__main__':
    app.run(debug=True)
