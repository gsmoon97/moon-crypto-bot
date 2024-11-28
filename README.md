# Moon's Crypto Bot 🌚

**Moon's Crypto Bot** is an automated cryptocurrency trading bot designed to trade **BTC/KRW** on Upbit. The bot uses the **CCXT library** to place limit buy orders at predefined percentage dips from the daily open price and manages funds dynamically based on successful orders. Notifications are sent via Telegram to keep you updated on trading activities.

---

## **Features**

- Automatically places limit buy orders for **BTC/KRW** at specific percentage dips (e.g., 1%, 2%, ..., 15%) from the daily open price.
- Customizable **minimum and maximum percentage dips** via `.env` file.
- Dynamically calculates and monitors available funds required for trading.
- Cancels unfilled orders before the next trading cycle.
- Sends real-time notifications to your Telegram bot for:
  - Order placements.
  - Order cancellations.
  - Insufficient funds warnings.
  - Filled orders and fund availability updates.

---

## **Project Structure**

```
.
├── .env                   # Environment variables
├── orders.py              # Handles placing, canceling, and monitoring orders
├── scheduler.py           # Manages daily tasks and Telegram notifications
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## **Setup Instructions**

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/moons-crypto-bot.git
cd moons-crypto-bot
```

### 2. Install Dependencies
Ensure you have Python 3.9+ installed. Install required dependencies using:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root directory and add the following:

```plaintext
# Upbit API Keys
UPBIT_ACCESS_KEY=your_upbit_access_key
UPBIT_SECRET_KEY=your_upbit_secret_key

# Telegram Bot Details
TELEGRAM_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id

# Trading Settings
MIN_PERCENTAGE_DIP=1        # Minimum percentage dip to buy
MAX_PERCENTAGE_DIP=15       # Maximum percentage dip to buy
```

- Replace `your_upbit_access_key` and `your_upbit_secret_key` with your Upbit API credentials.
- Replace `your_telegram_bot_token` and `your_telegram_chat_id` with your Telegram bot token and chat ID.

### 4. Run the Bot
Start the bot by running:
```bash
python scheduler.py
```

---

## **How It Works**

### Daily Schedule

1. **00:05 UTC: Place Orders**
   - The bot fetches the daily open price of **BTC/KRW** and places limit buy orders at percentage dips specified by `MIN_PERCENTAGE_DIP` and `MAX_PERCENTAGE_DIP`.

2. **Real-Time Monitoring**
   - The bot monitors placed orders continuously.
   - When an order is filled, it triggers a funds check and notifies you via Telegram.

3. **23:55 UTC: Cancel Remaining Orders**
   - Any unfilled orders are canceled before the next trading cycle.
   - If insufficient funds are detected for the next day, a warning notification is sent.

---

## **Customization**

### Adjusting Percentage Dips
Modify the percentage dips by updating `MIN_PERCENTAGE_DIP` and `MAX_PERCENTAGE_DIP` in the `.env` file. For example:
- To trade between 5% and 10% dips:
  ```plaintext
  MIN_PERCENTAGE_DIP=5
  MAX_PERCENTAGE_DIP=10
  ```

### Notification Settings
The bot uses Telegram to notify you of:
- Placed and canceled orders.
- Filled orders.
- Insufficient funds.

Ensure your Telegram bot token and chat ID are correctly configured in the `.env` file.

---

## **Dependencies**

- Python 3.9+
- [CCXT](https://github.com/ccxt/ccxt) – Cryptocurrency exchange trading library.
- [APScheduler](https://apscheduler.readthedocs.io/) – Scheduling library for running tasks.
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) – Telegram bot integration.

Install all dependencies via:
```bash
pip install -r requirements.txt
```

### `requirements.txt`
```plaintext
ccxt
apscheduler
python-telegram-bot
python-dotenv
```

---

## **Limitations**

- **Exchange API Limitations**: Ensure your Upbit API allows sufficient requests for order placements and status monitoring.
- **Trading Fees**: The bot does not account for trading fees, so ensure you have additional funds available.
- **Telegram Notification Lag**: Notifications depend on Telegram API response times, which may cause slight delays.

---

## **Troubleshooting**

### Common Errors
1. **`ModuleNotFoundError`**: Ensure all dependencies are installed using `pip install -r requirements.txt`.
2. **Insufficient Funds Warning**: Ensure your Upbit account has enough KRW to cover the required funds for the next day’s orders.
3. **Order Placement Errors**: Verify your Upbit API credentials and check the `MIN_PERCENTAGE_DIP` and `MAX_PERCENTAGE_DIP` settings.

### Debugging Tips
- Use `print()` statements in `orders.py` and `scheduler.py` to debug.
- Check Telegram notifications for details on errors or warnings.

---

## **Future Improvements**

- **Dynamic Order Amounts**: Allow users to configure order sizes for specific percentage dips.
- **Support for Multiple Pairs**: Extend the bot to trade other currency pairs.
- **WebSocket Integration**: Use WebSocket APIs for faster and more efficient order status monitoring.

---

## **License**

This project is open-source and available under the [MIT License](LICENSE).

---

Feel free to reach out if you encounter any issues or have feature requests. Happy trading! 🚀