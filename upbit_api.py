import requests


class UpbitAPI:
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key

    def get_historical_data(self):
        url = "https://api.upbit.com/v1/candles/days"
        params = {
            "market": "KRW-BTC",
            "count": 30,
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.json()}")
            return None

    def check_balance(self):
        url = "https://api.upbit.com/v1/accounts"
        headers = {
            "Access-Key": self.access_key,
            "Secret-Key": self.secret_key
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            balances = response.json()
            return next((float(balance['balance']) for balance in balances if balance['currency'] == 'KRW'), 0)
        else:
            print(f"Failed to retrieve balance: {response.json()}")
            return 0

    def buy_bitcoin(self):
        url = "https://api.upbit.com/v1/orders"
        headers = {
            "Access-Key": self.access_key,
            "Secret-Key": self.secret_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "market": "KRW-BTC",
            "side": "bid",
            "price": 5000,
            "ord_type": "limit"
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            return "Purchase successful"
        else:
            return f"Purchase failed: {response.json()}"
