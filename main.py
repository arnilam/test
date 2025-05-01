@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # 요청 내용 확인 로그
        print("💡 raw body:", request.data)
        print("💡 JSON:", request.json)

        data = request.json
        if not data:
            print("❗ request.json이 None입니다.")
            return jsonify({"error": "no payload received"}), 400

        symbol = data.get('symbol')
        side = data.get('side')
        qty = data.get('qty')

        print(f"📦 symbol: {symbol}, side: {side}, qty: {qty}")

        if not symbol or not side or not qty:
            print("❗ 필수 항목이 누락되었습니다.")
            return jsonify({"error": "missing one or more required fields"}), 400

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

        full_url = f"{url}?{sorted_params}&sign={sign}"
        print("🔗 요청 URL:", full_url)

        res = requests.post(full_url, json={}, headers=headers)
        print("📦 응답 일부:", res.text[:300])

        try:
            return jsonify(res.json())
        except Exception as e:
            print("❌ JSON 파싱 실패:", e)
            return jsonify({"error": "Invalid JSON", "raw": res.text[:300]}), 500

    except Exception as e:
        print("🔥 서버 에러:", e)
        return jsonify({"error": str(e)}), 500
