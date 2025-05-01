from flask import Flask, request, jsonify
import time
import hashlib
import hmac
import requests

app = Flask(__name__)

API_KEY = 'kbVWLk5AtPkCOSOVnk'
API_SECRET = 'uiWO9NHqgEbQCbdb4SSsHEP6cTOyqvKL45jT'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("🚀 받은 데이터:", data)

        symbol = data.get('symbol')
        side = data.get('side')
        qty = data.get('qty')

        url = 'https://api-testnet.bybit.com/v5/order/create'
        timestamp = str(int(time.time() * 1000))
        recvWindow = '5000'

        # ✅ params는 반드시 먼저 선언되어야 함!
        params = {
            "category": "linear",
            "symbol": symbol,
            "side": side,
            "orderType": "Market",
            "qty": str(qty),
            "timeInForce": "GoodTillCancel",
            "timestamp": timestamp,
            "recvWindow": recvWindow
        }

        sorted_params = '&'.join([f"{k}={params[k]}" for k in sorted(params)])
        sign = hmac.new(bytes(API_SECRET, 'utf-8'), bytes(sorted_params, 'utf-8'), hashlib.sha256).hexdigest()

        headers = {
            "X-BYBIT-API-KEY": API_KEY,
            "Content-Type": "application/json"
        }

        # ✅ 최종 요청
        res = requests.post(f"{url}?{sorted_params}&sign={sign}", json={}, headers=headers)
        print("📦 Bybit 응답:", res.text)
        return jsonify(res.json())

    except Exception as e:
        print("🔥 오류 발생:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return '✅ Flask 서버 작동 중!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
