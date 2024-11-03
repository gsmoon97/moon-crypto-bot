import os
import numpy as np
from dotenv import load_dotenv
from upbit_api import UpbitAPI
from telegram_bot import TelegramBot
from scheduler import PurchaseScheduler

# Load environment variables from .env file
load_dotenv()

# Initialize API keys and bot
UPBIT_ACCESS_KEY = os.getenv('UPBIT_ACCESS_KEY')
UPBIT_SECRET_KEY = os.getenv('UPBIT_SECRET_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

upbit_api = UpbitAPI(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
telegram_bot = TelegramBot(TELEGRAM_TOKEN, CHAT_ID)
purchase_scheduler = PurchaseScheduler(upbit_api)

def analyze_data(data):
    prices = {str(hour).zfill(2): [] for hour in range(24)}

    for candle in data:
        timestamp = candle['candle_date_time_utc']
        price = candle['trade_price']
        hour = int(timestamp[11:13])
        
        prices[str(hour).zfill(2)].append(price)

    avg_prices = {hour: np.mean(prices[hour]) for hour in prices if prices[hour]}
    optimal_hours = sorted(avg_prices, key=avg_prices.get)[:2]
    return optimal_hours

def schedule_dca():
    historical_data = upbit_api.get_historical_data()
    if historical_data:
        optimal_hours = analyze_data(historical_data)

        krw_balance = upbit_api.check_balance()
        if krw_balance <= 50000:
            telegram_bot.send_message("Your cash balance is below 50,000 KRW. Please deposit more funds.")

        purchase_scheduler.schedule_purchase(optimal_hours)
        telegram_bot.send_message(f"DCA strategy has started. Bitcoin will be purchased at {', '.join(optimal_hours)}:00 based on historical data.")
    else:
        telegram_bot.send_message("Failed to retrieve historical data.")

if __name__ == '__main__':
    schedule_dca()
