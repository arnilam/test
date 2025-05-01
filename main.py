from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    return jsonify({"message": f"Received {data}"})

@app.route('/')
def home():
    return '✅ Flask 서버 작동 중!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
