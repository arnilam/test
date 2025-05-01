from flask import Flask, request, jsonify
import time
import hashlib
import hmac
import requests

app = Flask(__name__)

# 테스트용 Bybit API 키 (실제 환경에서는 환경변수로 분리하세요)
API_KEY = 'kbVWLk5AtPkCOSOVnk'
API_SECRET = 'uiWO9NHqgEbQCbdb4SSsHEP6cTOyqvKL45jT'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # 1) 들어온 요청 원본 확인
        print("🟡 raw body:", request.data)
        print("🟡 parsed JSON:", request.json)

        data = request.json
        if not data:
            print("🔴 JSON payload가 없습니다.")
            return jsonify({"error": "no payload received"}), 400

        # 2) 필수 필드 추출 및 확인
        symbol = data.get('symbol')
        side   = data.get('side')
        qty    = data.get('qty')
        print(f"🟢 symbol: {symbol}, side: {side}, qty: {qty}")

        if not symbol or not side or not qty:
            print("🔴 missing one or more required fields")
            return jsonify({"error": "missing one or more required fields"}), 400

        # 3) Bybit 주문 준비
        url = 'https://api-testnet.bybit.com/v5/order/create'
        timestamp  = str(int(time.time() * 1000))
        recvWindow = '5000'

        params = {
            "category":     "linear",
            "symbol":       symbol,
            "side":         side,
            "orderType":    "Market",
            "qty":          str(qty),
            "timeInForce":  "GoodTillCancel",
            "timestamp":    timestamp,
            "recvWindow":   recvWindow
        }

        # 4) 쿼리스트링 정렬 및 서명 생성
        sorted_params = '&'.join(f"{k}={params[k]}" for k in sorted(params))
        sign = hmac.new(
            API_SECRET.encode('utf-8'),
            sorted_params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "X-BYBIT-API-KEY": API_KEY,
            "Content-Type":    "application/json"
        }

        full_url = f"{url}?{sorted_params}&sign={sign}"
        print("🔗 요청 URL:", full_url)

        # 5) 주문 요청 (쿼리로 파라미터 전달, 바디는 빈 JSON)
        res = requests.post(full_url, json={}, headers=headers)
        print("📦 Bybit 응답 (일부):", res.text[:300])

        # 6) 응답 JSON 파싱 및 반환
        try:
            return jsonify(res.json())
        except Exception as e:
            print("❌ JSON 파싱 실패:", e)
            return jsonify({"error": "Invalid JSON", "raw": res.text[:300]}), 500

    except Exception as e:
        print("🔥 서버 내부 오류:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return '✅ Flask 서버 작동 중!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
