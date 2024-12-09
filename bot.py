# bot.py
import ccxt
from decimal import Decimal
from dotenv import load_dotenv
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

# Command handler: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("User %s started the bot.", update.effective_user.username)
    
    # Define all available commands
    commands_list = """
Hello! This is Moon's Crypto Bot 🌚

Here are the commands you can use:
/start - Start the bot and see available commands
/check - See all your balances
/place - Place buy orders based on the dip-buy strategy
/cancel - Cancel all your open orders
"""
    
    # Send the message with available commands
    await update.message.reply_text(commands_list)

# Command handler: /check
async def check_balances(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Fetch balances from Upbit
        balance = upbit.fetch_balance()
        non_zero_balances = {
            asset: amount for asset, amount in balance.get('total', {}).items() if amount > 0
        }

        # Format balances for the message
        if non_zero_balances:
            balance_message = "Your balances:\n" + "\n".join(
                [f"{asset}: {amount:,.8f}" for asset, amount in non_zero_balances.items()]
            )
        else:
            balance_message = "You have no balances 🌚"

        # Send the message
        logger.info("Non-zero balances fetched successfully.")
        await update.message.reply_text(balance_message)
    except Exception as e:
        logger.error("Error fetching balances: %s", e)
        await update.message.reply_text("Failed to fetch balances. Please try again later 🌝")

# Function to get today's open price of BTC/KRW
def get_open_price():
    try:
        ticker = upbit.fetch_ticker("BTC/KRW")
        open_price = ticker["open"]
        logger.info(f"Fetched open price: {open_price} KRW")
        return open_price
    except Exception as e:
        logger.error(f"Error fetching open price: {e}")
        raise

# Function to round the price to the nearest 1,000 KRW
def round_upbit_price(price):
    return round(price / 1000) * 1000

# Command handler: /place
async def place_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        open_price = get_open_price()
        
        if open_price is None:
            await update.message.reply_text("Failed to retrieve the open price 🌝")
            return

        logger.info(f"Open price: {open_price}")
        placed_order_ids = []
        placed_order_details = []  # Collect details to show to the user
        
        # Iterate over the percentage dips
        for percentage_dip, krw in enumerate(
            range(6000, 6000 + (MAX_PERCENTAGE_DIP - MIN_PERCENTAGE_DIP + 1) * 1000, 1000),
            start=MIN_PERCENTAGE_DIP
        ):
            price = open_price * (1 - percentage_dip / 100)  # Use float calculations
            price = round_upbit_price(price)  # Round price to nearest 1000 KRW
            amount = round(krw / price, 8)  # Calculate the BTC amount using float
            logger.info(f"Price: {price} | Amount: {amount} BTC")
            order = upbit.create_limit_buy_order("BTC/KRW", amount, price)  # Use float for the API
            placed_order_ids.append(order["id"])  # Keep internal order IDs for logging

            # Format output for user
            placed_order_details.append(
                f"- {percentage_dip}% Dip: {amount} BTC at {price:,.0f} KRW (KRW {krw:,.0f})"
            )
            logger.info(f"Placed order: {order['id']} | Price: {price} | Amount: {amount} BTC")

        logger.info("All orders placed successfully.")
        await update.message.reply_text(f"Placed {len(placed_order_ids)} orders:\n" + "\n".join(placed_order_details))
    except Exception as e:
        logger.error(f"Error placing orders: {e}")
        await update.message.reply_text("An error occurred while placing orders. Please try again later 🌝")

# Add this command handler for /cancel
async def cancel_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Fetch open orders
        open_orders = upbit.fetch_open_orders("BTC/KRW")  # Fetch open orders for BTC/KRW
        if not open_orders:
            await update.message.reply_text("No open orders to cancel 🌚")
            return
        
        # Cancel each open order
        canceled_order_ids = []
        canceled_order_details = []  # Collect details to show to the user

        for order in open_orders:
            order_id = order['id']
            upbit.cancel_order(order_id)  # Cancel the order
            canceled_order_ids.append(order_id)  # Keep internal order IDs for logging
            logger.info(f"Cancelled order: {order_id}")

            # Calculate percentage dip (reverse the open price logic)
            original_price = get_open_price()  # Get open price for calculation
            percentage_dip = round((1 - float(order["price"]) / original_price) * 100)  # % dip

            # Format output for the user
            canceled_order_details.append(
                f"- {percentage_dip}% Dip: {order['amount']} BTC at {float(order['price']):,.0f} KRW"
            )
            logger.info(f"Canceled order: {order['id']} | Price: {order['price']} | Amount: {order['amount']} BTC")
        
        # Inform the user about the canceled orders
        logger.info("All open orders canceled successfully.")
        await update.message.reply_text(f"Canceled {len(canceled_order_ids)} orders:\n" + "\n".join(canceled_order_details))
    except Exception as e:
        logger.error(f"Error canceling orders: {e}")
        await update.message.reply_text("An error occurred while canceling orders. Please try again later 🌝")

# Function to automatically trigger a task at a scheduled time (UTC+0)
def scheduled_task(task_name, task_function):
    logger.info(f"Scheduled {task_name} task triggered.")
    
    async def run_task():
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        class DummyUpdate:
            def __init__(self):
                self.message = type('obj', (object,), {'reply_text': lambda self, text: print(text)})
        
        dummy_update = DummyUpdate()
        await task_function(dummy_update, None)
    
    return run_task

# Start scheduling in a separate thread 
def start_scheduling():
    schedule.every().day.at("00:05").do(scheduled_task("place orders", place_orders))
    schedule.every().day.at("23:55").do(scheduled_task("cancel orders", cancel_orders))

    while True:
        schedule.run_pending()  # Check if any scheduled task is due
        time.sleep(1)  # Sleep for a second

# Main function
def main():
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
    scheduler_thread = threading.Thread(target=start_scheduling, daemon=True)
    scheduler_thread.start()

    # Start the bot
    logger.info("Bot started successfully.")
    application.run_polling()

if __name__ == "__main__":
    main()