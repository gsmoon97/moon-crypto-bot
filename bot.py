import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from orders import place_orders, cancel_orders
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CHAT_ID = os.getenv("CHAT_ID")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello there! This is Moon's Crypto Bot 🌚")

async def place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = place_orders()
        await context.bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"Error placing orders: {e}")
        await context.bot.send_message(chat_id=CHAT_ID, text=f"Error placing orders: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = cancel_orders()
        await context.bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"Error canceling orders: {e}")
        await context.bot.send_message(chat_id=CHAT_ID, text=f"Error canceling orders: {e}")

if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("place", place))
    application.add_handler(CommandHandler("cancel", cancel))

    application.run_polling()
