from flask import Flask, request, jsonify
import time
import hashlib
import hmac
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get('kbVWLk5AtPkCOSOVnk')
API_SECRET = os.environ.get('uiWO9NHqgEbQCbdb4SSsHEP6cTOyqvKL45jT')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    symbol = data['symbol']
    side = data['side']
    qty = data['qty']

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
    sign = hmac.new(bytes(API_SECRET, 'utf-8'), bytes(sorted_params, 'utf-8'), hashlib.sha256).hexdigest()
    params["sign"] = sign

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    res = requests.post(url, json=params, headers=headers)
    return jsonify(res.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
