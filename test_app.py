#!/usr/bin/env python3
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# Logging removed for testing

@app.route('/')
def hello():
    return "Flask is working!"

@app.route('/test')
def test():
    return "Test page"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)