# Moon's Crypto Bot 🌚

A Telegram bot for automated crypto trading on Upbit. It places dip-buy orders for Bitcoin (BTC) based on configurable price percentages and manages orders directly through Telegram commands.

The bot uses a **3-tier microservices architecture** with separate components for Telegram UI, scheduling, and exchange integration.

---

## Features

- **Check Balances:** View your non-zero balances on Upbit.
- **Place Orders:** Place buy orders at predefined price dips (manual or scheduled).
- **Cancel Orders:** Cancel open orders and view statistics on filled orders.
- **Check Orders:** View all currently open bot-created orders.
- **Automated Scheduling:** Start/stop daily automated order placement and cancellation.
- **Telegram Integration:** Use a command-based menu for easy operation.
- **Order Tracking:** SQLite database tracks all orders for audit purposes.

---

## Architecture

The bot consists of three independent components:

1. **Exchange Bot** (`exchange_bot.py`) - Flask REST API on port 5000

   - Handles Upbit exchange integration via CCXT
   - Manages order placement, cancellation, and tracking
   - Maintains SQLite database for order history

2. **Schedule Bot** (`schedule_bot.py`) - Flask REST API on port 6000

   - Manages automated daily scheduling using APScheduler
   - Places orders at `START_TIME` and cancels at `END_TIME`
   - Sends Telegram notifications for scheduled tasks

3. **Telegram Bot** (`telegram_bot.py`) - Telegram interface
   - Provides user-facing command interface
   - Routes commands to Exchange and Schedule APIs
   - Displays formatted responses to users

---

## Requirements

- **Python 3.8 to 3.12**
  - **Not compatible with Python 3.13** due to a known issue with the `Updater` class in the `python-telegram-bot` library when running on Python 3.13
- An Upbit API key (with permissions for trading)
- A Telegram bot token
- `pip` for installing dependencies

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
# Exchange Credentials
UPBIT_ACCESS_KEY=your_upbit_access_key
UPBIT_SECRET_KEY=your_upbit_secret_key

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_chat_id

# Order Parameters
START_PERCENTAGE_DIP=1
END_PERCENTAGE_DIP=25
START_AMOUNT=6000
AMOUNT_INCREMENT=1000

# Scheduling Times
START_TIME=00:05
END_TIME=23:55

# API URLs (optional, defaults to localhost)
EXCHANGE_API_URL=http://localhost:5000
SCHEDULE_API_URL=http://localhost:6000
```

### 5. Run the Bots

Use the provided `run.sh` script to start all three components:

```bash
chmod +x run.sh
./run.sh
```

This will start:

1. Exchange Bot on port 5000
2. Schedule Bot on port 6000
3. Telegram Bot (polling mode)

All bots will run in the background, with logs written to:

- `exchange_bot.log`
- `schedule_bot.log`
- `telegram_bot.log`

**Note:** The script waits for health checks on each API before starting the next component.

---

## Available Commands

| Command            | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| `/start`           | Display the list of available commands.                      |
| `/check_balances`  | Check your current non-zero balances on Upbit.               |
| `/place_orders`    | Manually place dip-buy orders based on configured strategy.  |
| `/cancel_orders`   | Cancel all open orders and show statistics on filled orders. |
| `/check_orders`    | View all currently open bot-created orders.                  |
| `/start_scheduler` | Start automated daily order placement and cancellation.      |
| `/stop_scheduler`  | Stop automated daily scheduling.                             |

---

## Log Management

Each component has its own rotating log file (max size: 5MB, 5 backups):

- `exchange_bot.log` - Exchange API operations and Upbit interactions
- `schedule_bot.log` - Scheduled task execution and APScheduler events
- `telegram_bot.log` - Telegram command handling and user interactions

To view logs in real-time:

```bash
# View all logs
tail -f exchange_bot.log schedule_bot.log telegram_bot.log

# View specific component
tail -f telegram_bot.log
```

**Order History Database:**

- `order_tracker.db` - SQLite database tracking all created and filled orders

---

## Automated Scheduling

The Schedule Bot (`schedule_bot.py`) can automatically:

1. Place dip-buy orders daily at `START_TIME` (default: 00:05)
2. Cancel all open orders daily at `END_TIME` (default: 23:55)

**To enable automated scheduling:**

1. Send `/start_scheduler` command in Telegram
2. The bot will confirm scheduling is active
3. Orders will be placed/cancelled daily at configured times

**To disable automated scheduling:**

- Send `/stop_scheduler` command in Telegram

**Manual control:**

- You can still manually place/cancel orders using `/place_orders` and `/cancel_orders` commands regardless of scheduler status

**Configuration:**

- Adjust `START_TIME` and `END_TIME` in the `.env` file
- Restart the Schedule Bot for changes to take effect

---

## Development Notes

### Tech Stack

- **Exchange Integration:** `ccxt` library for Upbit API
- **Telegram Bot:** `python-telegram-bot` library
- **REST APIs:** Flask framework
- **Scheduling:** APScheduler for background jobs
- **Database:** SQLite for order tracking
- **Configuration:** `python-dotenv` for environment variables

### Architecture Benefits

- **Modularity:** Each component can be developed, tested, and deployed independently
- **Scalability:** REST APIs allow easy horizontal scaling
- **Maintainability:** Clear separation of concerns (UI, scheduling, exchange logic)
- **Reliability:** Component failures are isolated

### API Endpoints

**Exchange Bot (port 5000):**

- `GET /health` - Health check
- `GET /check_balances` - Get non-zero account balances
- `POST /place_orders` - Create limit buy orders
- `POST /cancel_orders` - Cancel open orders
- `GET /check_orders` - List all open bot orders

**Schedule Bot (port 6000):**

- `GET /health` - Health check
- `POST /start_scheduler` - Start daily job scheduler
- `POST /stop_scheduler` - Stop job scheduler

---

## Contribution

Contributions are welcome! Fork the repository, submit issues, or open pull requests to help improve the bot.

---

## Disclaimer

This bot is intended for educational purposes only. Use at your own risk. Ensure compliance with your local laws and regulations regarding cryptocurrency trading.
