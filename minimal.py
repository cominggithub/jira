from flask import Flask, request
from datetime import datetime
app = Flask(__name__)

@app.after_request
def log_requests(response):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {request.method} {request.path} - {request.remote_addr}"
    print(f"REQUEST: {log_msg}")
    with open('requests.log', 'a') as f:
        f.write(f"{log_msg}\n")
    return response

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)