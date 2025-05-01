from flask import Flask, request, jsonify
import time
import hashlib
import hmac
import requests

app = Flask(__name__)

# 테스트용 직접 입력 방식 (추후 환경변수로 대체 가능)
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

        # 쿼리 스트링 만들기 & 서명 생성
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

        # 실제 요청 (쿼리로 보내고 바디는 비움)
        full_url = f"{url}?{sorted_params}&sign={sign}"
        res = requests.post(full_url, json={}, headers=headers)

        # 응답 출력 (길이 제한)
        print("📦 응답 일부:", res.text[:300])

        # 응답이 JSON 형식이면 반환
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
