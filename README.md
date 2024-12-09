# Moon's Crypto Bot 🌚  

A Telegram bot for automated crypto trading on Upbit. It places dip-buy orders for Bitcoin (BTC) based on configurable price percentages and manages orders directly through Telegram commands.  

---

## Features  
- **Check Balances:** View your non-zero balances on Upbit.  
- **Place Orders:** Automatically place buy orders at predefined price dips.  
- **Cancel Orders:** Cancel open orders created by the bot.  
- **Scheduled Tasks:** Automatically place and cancel orders at specific times.  
- **Telegram Integration:** Use a command-based menu for easy operation.  

---

## Requirements  
- Python 3.8+  
- An Upbit API key (with permissions for trading).  
- A Telegram bot token.  
- `pip` for installing dependencies.  

---

## Setup  

### 1. Clone the Repository  
```bash  
git clone <repository-url>  
cd <repository-directory>  
```  

### 2. Create a Virtual Environment  
```bash  
python -m venv .venv  
source .venv/bin/activate  # On Windows: .venv\Scripts\activate  
```  

### 3. Install Dependencies  
```bash  
pip install -r requirements.txt  
```  

### 4. Set Environment Variables  
Create a `.env` file in the project root with the following keys:  
```env  
UPBIT_ACCESS_KEY=your_upbit_access_key  
UPBIT_SECRET_KEY=your_upbit_secret_key  
TELEGRAM_BOT_TOKEN=your_telegram_bot_token  
CHAT_ID=your_telegram_chat_id  

MIN_PERCENTAGE_DIP=1  
MAX_PERCENTAGE_DIP=10  
MIN_AMOUNT=6000  
AMOUNT_INCREMENT=1000  

START_TIME=00:05  
END_TIME=23:55  
```  

### 5. Run the Bot  
Use the provided `run.sh` script to start the bot:  
```bash  
chmod +x run.sh  
./run.sh  
```  

The bot will run in the background, and logs will be written to `bot.log`.  

---

## Available Commands  
| Command   | Description |  
|-----------|-------------|  
| `/start`  | Display the list of available commands. |  
| `/check`  | Check your current non-zero balances. |  
| `/place`  | Place dip-buy orders based on the configured strategy. |  
| `/cancel` | Cancel all open orders created by the bot. |  

---

## Log Management  
Logs are stored in `bot.log` with a rotating file handler (max size: 5MB, 5 backups).  

To view logs:  
```bash  
tail -f bot.log  
```  

---

## Scheduling Tasks  
The bot automatically:  
1. Places orders daily at `START_TIME`.  
2. Cancels orders daily at `END_TIME`.  

These times can be adjusted in the `.env` file.  

---

## Development Notes  
- The bot uses the `ccxt` library for interacting with Upbit and the `python-telegram-bot` library for Telegram integration.  
- Commands are displayed in the Telegram chat menu for easy access.  

---

## Contribution  
Feel free to fork the repository, submit issues, or open pull requests to improve the bot.  

---

## Disclaimer  
This bot is intended for educational purposes only. Use at your own risk. Ensure compliance with your local laws and regulations regarding cryptocurrency trading.  