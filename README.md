# Moon's Crypto Bot 🌚

**Moon's Crypto Bot** is an automated cryptocurrency trading bot designed for **BTC/KRW** trading on the Upbit exchange. It places limit buy orders based on daily percentage dips, monitors balances, and provides real-time notifications via Telegram. 

---

## **Features**

- **Automated Dip Buying**: Places limit buy orders at percentage dips (e.g., 1%, 2%, ..., 15%) below the daily open price.
- **Balance Tracking**: Displays all non-zero balances in your Upbit account.
- **Order Management**: 
  - Automatically places and cancels orders on schedule.
  - Cancels unfilled orders at the end of the day.
- **Customizable Trading Parameters**: Define dip ranges and order sizes via `.env`.
- **Telegram Integration**: Real-time notifications for order placements, cancellations, and balance updates.

---

## **Commands**

- **`/start`**: View all available commands.
- **`/check`**: Check and display your non-zero account balances.
- **`/place`**: Place buy orders at predefined dips below the daily BTC/KRW open price.
- **`/cancel`**: Cancel all unfilled orders.

---

## **Daily Automation**

- **00:05 UTC**: Places orders based on the specified percentage dips.
- **23:55 UTC**: Cancels any unfilled orders to prepare for the next day.

---

## **Setup Instructions**

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/moons-crypto-bot.git
cd moons-crypto-bot
```

### 2. Install Dependencies
Ensure you have Python 3.9+ installed. Install required libraries using:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root with the following details:

```plaintext
# Upbit API Keys
UPBIT_ACCESS_KEY=your_upbit_access_key
UPBIT_SECRET_KEY=your_upbit_secret_key

# Telegram Bot Details
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id

# Trading Parameters
MIN_PERCENTAGE_DIP=1        # Minimum percentage dip
MAX_PERCENTAGE_DIP=15       # Maximum percentage dip
```

Replace the placeholders with your actual credentials.

---

## **Usage**

### Start the Bot
Run the bot locally with:
```bash
python bot.py
```

---

## **How It Works**

1. **Fetch Open Price**: Retrieves the daily BTC/KRW open price.
2. **Place Orders**: Places buy orders at dips between `MIN_PERCENTAGE_DIP` and `MAX_PERCENTAGE_DIP`.
3. **Cancel Orders**: Cancels all open orders at the end of the day.
4. **Notifications**: Sends updates via Telegram for every action.

---

## **Customization**

- Adjust percentage dips by modifying `MIN_PERCENTAGE_DIP` and `MAX_PERCENTAGE_DIP` in the `.env` file.
- Configure order sizes based on your strategy by modifying the predefined KRW amounts.

---

## **Dependencies**

Install dependencies using:
```bash
pip install -r requirements.txt
```

Dependencies include:
- **`ccxt`**: For interacting with the Upbit API.
- **`python-telegram-bot`**: Telegram bot integration.
- **`python-dotenv`**: To manage environment variables.

---

## **Limitations**

- **Exchange Fees**: The bot does not account for trading fees, so ensure extra funds are available.
- **API Limits**: Ensure your Upbit account has sufficient request limits.
- **Latency**: Telegram notifications may experience slight delays due to network or API issues.

---

## **Troubleshooting**

- **Dependency Issues**: Use `pip install -r requirements.txt` to ensure all dependencies are installed.
- **Insufficient Funds**: Ensure adequate funds are available for trading and fees.
- **Error Logs**: Check logs for detailed error messages.

---

## **Future Improvements**

- Dynamic order sizes.
- Support for additional trading pairs.
- Enhanced error handling and reporting. 

Start trading smartly with **Moon's Crypto Bot**! 🌚