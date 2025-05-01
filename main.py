from flask import Flask, request, jsonify
import time
import hashlib
import hmac
import requests

app = Flask(__name__)

# 테스트용 Bybit API 키 (실제 환경에서는 환경변수로 분리)
API_KEY = 'kbVWLk5AtPkCOSOVnk'
API_SECRET = 'uiWO9NHqgEbQCbdb4SSsHEP6cTOyqvKL45jT'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # 요청 내용 확인 로그
        print("💡 raw body:", request.data)
        print("💡 JSON:", request.json)

        data = request.json
        if not data:
            return jsonify({"error": "no payload received"}), 400

        symbol = data.get('symbol')
        side = data.get('side')
        qty = data.get('qty')

        if not symbol or not side or not qty:
            return jsonify({"error": "missing one or more required fields"}), 400

        # Bybit V5 주문 API (테스트넷)
        url = 'https://api-testnet.bybit.com/v5/order/create'
        timestamp = str(int(time.time() * 1000))
        recvWindow = '5000'

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

        # 파라미터 정렬 + 서명 생성
        sorted_params = '&'.join([f"{k}={params[k]}" for k in sorted(params)])
        sign = hmac.new(
            bytes(API_SECRET, 'utf-8'),
            bytes(sorted_params, 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "X-BYBIT-API-KEY": API_KEY,
            "Content-Type": "application/json"
        }

        # Bybit 요청
        full_url = f"{url}?{sorted_params}&sign={sign}"
        res = requests.post(full_url, json={}, headers=headers)

        print("📦 응답 일부:", res.text[:300])

        # 응답 JSON 반환
        try:
            return jsonify(res.json())
        except Exception as e:
            print("❌ JSON 파싱 실패:", e)
            return jsonify({"error": "Invalid JSON", "raw": res.text[:300]}), 500

    except Exception as e:
        print("🔥 서버 에러:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return '✅ Flask 서버 작동 중!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
