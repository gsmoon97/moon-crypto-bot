# Moon's Crypto Bot 🌚

Moon's Crypto Bot is a Telegram bot designed to automate cryptocurrency trading on Upbit. It includes a dip-buying strategy based on predefined percentage drops in the BTC/KRW market price, balance checks, and automated order management.

## Features
- **Command Interface:**
  - `/start`: View all available commands.
  - `/check`: Check your account balances.
  - `/place`: Place buy orders for BTC based on percentage dips.
  - `/cancel`: Cancel open orders created by the bot.
- **Automated Scheduling:**
  - Automatically place buy orders at a specified start time.
  - Automatically cancel open orders at a specified end time.
- **Rotating Logs:** Logs are maintained with a rotating file handler to prevent storage overflow.

---

## Setup

### 1. Prerequisites
- Python 3.8 or higher
- An Upbit account with API credentials
- A Telegram bot token
- `pip` for managing dependencies

### 2. Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/<your-repo>.git
    cd <your-repo>
    ```

2. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the project directory:
    ```bash
    touch .env
    ```

4. Add the following variables to the `.env` file:
    ```plaintext
    # Upbit API credentials
    UPBIT_ACCESS_KEY=<your_upbit_access_key>
    UPBIT_SECRET_KEY=<your_upbit_secret_key>
    
    # Telegram Bot API token
    TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
    CHAT_ID=<your_chat_id>
    
    # Dip-buying strategy
    MIN_PERCENTAGE_DIP=1
    MAX_PERCENTAGE_DIP=10
    
    # Scheduling times (UTC)
    START_TIME=00:05
    END_TIME=23:55
    ```

---

## Usage

### 1. Run the Bot
Start the bot with:
```bash
python bot.py
```

### 2. Interact with the Bot
Use the following Telegram commands:
- `/start`: View all available commands.
- `/check`: See your current account balances.
- `/place`: Place buy orders for BTC based on the dip-buying strategy.
- `/cancel`: Cancel open orders created by the bot.

### 3. Logs
Logs are written to `bot.log` with a maximum size of 5 MB per file. Up to 5 log files are retained for reference.

---

## Customization

### Update Dip-Buy Strategy
Modify the range of percentage dips (`MIN_PERCENTAGE_DIP` to `MAX_PERCENTAGE_DIP`) in the `.env` file.

### Scheduling
Adjust the `START_TIME` and `END_TIME` in the `.env` file to schedule tasks.

---

## Contributing
Feel free to fork the repository and submit pull requests for improvements or bug fixes.