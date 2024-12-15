from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import os
import requests
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
EXCHANGE_API_URL = "http://localhost:5000"  # REST API URL from exchange_bot.py

START_PERCENTAGE_DIP = float(os.getenv("START_PERCENTAGE_DIP", 1.0))
END_PERCENTAGE_DIP = float(os.getenv("END_PERCENTAGE_DIP", 10.0))
PERCENTAGE_DIP_INCREMENT = float(os.getenv("PERCENTAGE_DIP_INCREMENT", 1.0))
START_AMOUNT = int(os.getenv("START_AMOUNT", 6000))
AMOUNT_INCREMENT = int(os.getenv("AMOUNT_INCREMENT", 1000))

# Configure logging
log_file = "telegram_bot.log"
log_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG, 
    handlers=[log_handler]
)
logger = logging.getLogger(__name__)

# ---------------- Telegram Command Handlers ----------------
# Command handler: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("User %s started the bot.", update.effective_user.username)
    """Display available commands."""
    commands = """
Welcome to the Crypto Order Bot 🌚

Commands:
/start - See all commands
/check_balances - Check all balances
/place_orders - Place dip-buy orders
/cancel_orders - Cancel all open orders
/check_orders - Check all open orders
"""
    await update.message.reply_text(commands)

# Command handler: /check_balances
async def check_balances(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = requests.get(f"{EXCHANGE_API_URL}/check_balances")
        response.raise_for_status()  # Check for HTTP errors

        non_zero_balances = response.json().get('non_zero_balances', {})
        if non_zero_balances:
            balance_message = "Current balances:\n" + "\n".join(
                [f"{asset}: {amount:,.8g}" for asset, amount in non_zero_balances.items()]
            )
            await update.message.reply_text(balance_message)
        else:
            await update.message.reply_text("No balances 🌚")
        
    except Exception as e:
        logger.error(f"Error fetching balances: {e}")
        await update.message.reply_text("An error occurred while fetching orders. Please try again later 🌝")

# Command handler: /place_orders
async def place_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        payload = {
            "start_percentage_dip": START_PERCENTAGE_DIP,
            "end_percentage_dip": END_PERCENTAGE_DIP,
            "percentage_dip_increment": PERCENTAGE_DIP_INCREMENT,
            "start_amount": START_AMOUNT,
            "amount_increment": AMOUNT_INCREMENT,
        }
        response = requests.post(f"{EXCHANGE_API_URL}/place_orders", json=payload)
        response.raise_for_status()  # Check for HTTP errors

        placed_orders = response.json().get('placed_orders', [])
        if placed_orders:
            orders_message = f"Placed {len(placed_orders)} orders:\n" + "\n".join(
                [f"- {placed_order['percentage_dip']:.2f}% Dip: {placed_order['amount']:,.8f} BTC @ {placed_order['price']:,.0f} KRW" for placed_order in placed_orders]
            )
            await update.message.reply_text(orders_message)
        else:
            await update.message.reply_text("No orders were placed 🌚")
        
    except Exception as e:
        logger.error(f"Error placing orders: {e}")
        await update.message.reply_text("An error occurred while placing orders. Please try again later 🌝")

# Command handler: /cancel_orders
async def cancel_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = requests.post(f"{EXCHANGE_API_URL}/cancel_orders")
        response.raise_for_status()  # Check for HTTP errors

        cancelled_orders = response.json().get('cancelled_orders', [])
        if cancelled_orders:
            orders_message = f"Cancelled {len(cancelled_orders)} orders:\n" + "\n".join(
                [f"- {cancelled_order['percentage_dip']:.2f}% Dip: {cancelled_order['amount']:,.8f} BTC @ {cancelled_order['price']:,.0f} KRW" for cancelled_order in cancelled_orders]
            )
            await update.message.reply_text(orders_message)
        else:
            orders_message = "No orders were cancelled 🌚"

        filled_orders = response.json().get('filled_orders', [])
        if filled_orders:
            total_btc = sum(order["amount"] for order in filled_orders)
            total_cost = sum(order["amount"] * order["price"] for order in filled_orders)
            weighted_avg_price = total_cost / total_btc if total_btc > 0 else 0

            stats_message = (
                f"📊 Transaction Statistics:\n"
                f"- Total BTC Purchased: {total_btc:,.8f} BTC\n"
                f"- Weighted Average Price: {weighted_avg_price:,.0f} KRW/BTC\n"
            )
        else:
            stats_message = "No orders were filled 🌚"
        await update.message.reply_text(stats_message)
    except Exception as e:
        logger.error(f"Error cancelling orders: {e}")
        await update.message.reply_text("An error occurred while cancelling orders. Please try again later 🌝")

# Command handler: /check_orders
async def check_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = requests.get(f"{EXCHANGE_API_URL}/check_orders")
        response.raise_for_status()  # Check for HTTP errors

        open_orders = response.json().get('open_orders', [])

        if open_orders:
            orders_message = f"Current orders:\n" + "\n".join(
                [f"- {open_order['percentage_dip']:.2f}% Dip: {open_order['amount']:,.8f} BTC @ {open_order['price']:,.0f} KRW" for open_order in open_orders]
            )
            await update.message.reply_text(orders_message)
        else:
            await update.message.reply_text("No open orders 🌚")
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        await update.message.reply_text("An error occurred while fetching orders. Please try again later 🌝")

async def post_init(application: Application) -> None:
    """Set bot commands on startup."""
    bot = application.bot
    await bot.set_my_commands([
        BotCommand("start", "See all commands"),
        BotCommand("check_balances", "Check all balances"),
        BotCommand("place_orders", "Place dip-buy orders"),
        BotCommand("cancel_orders", "Cancel all open orders"),
        BotCommand("check_orders", "Check all open orders"),
    ])

# ---------------- Main Application ----------------
def main():
    """Start the Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Telegram bot token missing. Set TELEGRAM_BOT_TOKEN in .env")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # Add command handlers
    application.add_handlers([
        CommandHandler("start", start),
        CommandHandler("check_balances", check_balances),
        CommandHandler("place_orders", place_orders),
        CommandHandler("cancel_orders", cancel_orders),
        CommandHandler("check_orders", check_orders),
    ])

    logger.info("Telegram bot started successfully.")
    application.run_polling()

if __name__ == '__main__':
    main()
