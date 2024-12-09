# bot.py
import asyncio
import ccxt
from decimal import Decimal
from dotenv import load_dotenv
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import pytz
import schedule
from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading
import time

# Load environment variables
load_dotenv()

UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MIN_PERCENTAGE_DIP = int(os.getenv("MIN_PERCENTAGE_DIP", 1))
MAX_PERCENTAGE_DIP = int(os.getenv("MAX_PERCENTAGE_DIP", 10))

# File to persist order tracking data
ORDER_TRACKER_FILE = "order_tracker.json"

# Initialize the order tracker
order_tracker = []

# Configure logging with log rotation
log_file = "bot.log"
log_handler = RotatingFileHandler(
    log_file, maxBytes=5 * 1024 * 1024, backupCount=5  # 5 MB per file, keep 5 backups
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[log_handler]  # Use the rotating file handler
)

logger = logging.getLogger(__name__)

# Initialize Upbit exchange instance
upbit = ccxt.upbit({
    'apiKey': UPBIT_ACCESS_KEY,
    'secret': UPBIT_SECRET_KEY
})

# Load order tracker data from file
def load_order_tracker():
    try:
        if os.path.exists(ORDER_TRACKER_FILE):
            with open(ORDER_TRACKER_FILE, 'r') as file:
                return json.load(file)
        return []
    except Exception as e:
        logger.error(f"Error loading order tracker: {e}")
        return []

# Save order tracker data to file
def save_order_tracker():
    try:
        with open(ORDER_TRACKER_FILE, 'w') as file:
            json.dump(order_tracker, file, indent=4)
        logger.info("Order tracker saved successfully.")
    except Exception as e:
        logger.error(f"Error saving order tracker: {e}")

# Get today's open price of BTC/KRW
def get_open_price():
    try:
        ticker = upbit.fetch_ticker("BTC/KRW")
        return Decimal(ticker["open"])
    except Exception as e:
        logger.error(f"Error fetching open price: {e}")
        return None

# Round price for Upbit
def round_upbit_price(price):
    return Decimal(price).quantize(Decimal("1000"))

# Command handler: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("User %s started the bot.", update.effective_user.username)
    
    # Define all available commands
    commands_list = """
    Hello! This is Moon's Crypto Bot 🌚
    
    Commands:
    /start - Start the bot
    /check - Check your balances
    /place - Place dip-buy orders
    /cancel - Cancel orders
    """
    await update.message.reply_text(commands_list)

# Command handler: /check
async def check_balances(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Fetch balances from Upbit
        balance = upbit.fetch_balance()
        non_zero_balances = {
            asset: amount for asset, amount in balance.get('total', {}).items() if amount > 0
        }

        # Send the message
        balance_message = "Your balances:\n" + "\n".join(
            [f"{asset}: {amount:,.8f}" for asset, amount in non_zero_balances.items()]
        ) if non_zero_balances else "You have no balances 🌚"
        await update.message.reply_text(balance_message)
    except Exception as e:
        logger.error("Error fetching balances: %s", e)
        await update.message.reply_text("Failed to fetch balances. Please try again later 🌝")

# Command handler: /place
async def place_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global order_tracker
    try:
        open_price = get_open_price()
        if not open_price:
            await update.message.reply_text("Failed to retrieve the open price 🌝")
            return
        
        details = []  # Collect details to show to the user
        # Iterate over the percentage dips
        for percentage_dip in range(MIN_PERCENTAGE_DIP, MAX_PERCENTAGE_DIP + 1):
            price = round_upbit_price(open_price * (1 - Decimal(percentage_dip) / 100))
            krw = Decimal(6000 + (percentage_dip - MIN_PERCENTAGE_DIP) * 1000)
            amount = krw / price
            order = upbit.create_limit_buy_order("BTC/KRW", float(amount), float(price))
            order_tracker.append({"id": order["id"], "price": float(price), "amount": float(amount)})
            details.append(f"{percentage_dip}% Dip: {amount} BTC @ {price} KRW")

        save_order_tracker()  # Save tracker after placing orders
        await update.message.reply_text(f"Placed {len(details)} orders:\n" + "\n".join(details))
    except Exception as e:
        logger.error(f"Error placing orders: {e}")
        await update.message.reply_text("An error occurred while placing orders. Please try again later 🌝")

# Command handler: /cancel
async def cancel_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global order_tracker
    try:
        open_orders = upbit.fetch_open_orders("BTC/KRW")
        if not open_orders:
            await update.message.reply_text("No open orders to cancel 🌚")
            return
        
        details = []  # Collect details to show to the user
        # Iterate over open orders placed by /place command
        for order in open_orders:
            if order["id"] in [o["id"] for o in order_tracker]:
                upbit.cancel_order(order["id"])
                details.append(f"Canceled: {order['price']} KRW")
        save_order_tracker()
        await update.message.reply_text("Canceled orders:\n" + "\n".join(details))
    except Exception as e:
        logger.error(f"Error canceling orders: {e}")
        await update.message.reply_text("An error occurred while canceling orders. Please try again later 🌝")

# Automatically trigger a task at a scheduled time
async def scheduled_task(task_function, application):
    try:
        logger.info(f"Scheduled task triggered: {task_function.__name__}")
        
        # Use a dummy update object to invoke handlers
        class DummyUpdate:
            def __init__(self):
                self.message = type('obj', (object,), {'reply_text': lambda _, text: logger.info(text)})
        
        dummy_update = DummyUpdate()
        await task_function(dummy_update, None)
    except Exception as e:
        logger.error(f"Error in scheduled task {task_function.__name__}: {e}")

# Start scheduling tasks
def start_scheduling(application):
    start_time = os.getenv("START_TIME", "00:05")  # Default to 00:05 if not provided
    end_time = os.getenv("END_TIME", "23:55")     # Default to 23:55 if not provided
    
    schedule.every().day.at(start_time).do(
        lambda: asyncio.run(scheduled_task(place_orders, application))
    )
    schedule.every().day.at(end_time).do(
        lambda: asyncio.run(scheduled_task(cancel_orders, application))
    )

    while True:
        schedule.run_pending()
        time.sleep(1)

# Main function
def main():
    global order_tracker
    load_order_tracker()  # Load tracker on startup
    
    # Check if the Telegram token is set
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Telegram bot token not found in environment variables.")
        return

    # Initialize Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Set bot commands for the menu button
    commands = [
        BotCommand("start", "Start the bot and see available commands"),
        BotCommand("check", "See all your balances"),
        BotCommand("place", "Place buy orders based on the dip-buy strategy"),
        BotCommand("cancel", "Cancel all your open orders"),
    ]
    application.bot.set_my_commands(commands)

    # Add command handlers
    application.add_handler(CommandHandler("start", start))  # /start command
    application.add_handler(CommandHandler("check", check_balances))  # /check command
    application.add_handler(CommandHandler("place", place_orders))  # /place command
    application.add_handler(CommandHandler("cancel", cancel_orders))  # /cancel command

    # Start scheduling in a separate thread
    scheduler_thread = threading.Thread(target=start_scheduling, args=(application,), daemon=True)
    scheduler_thread.start()

    # Start the bot
    logger.info("Bot started successfully.")
    application.run_polling()

if __name__ == "__main__":
    main()