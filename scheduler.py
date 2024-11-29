# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from orders import place_orders, cancel_orders, check_funds, monitor_filled_orders
from telegram import Bot
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_TOKEN)


async def notify_user(message):
    """Send a message to the user via Telegram."""
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        logger.info(f"Notification sent: {message}")
    except Exception as e:
        logger.error(f"Error notifying user: {e}")


async def check_funds_and_notify():
    """Check if sufficient funds are available and notify the user."""
    try:
        has_funds, message = check_funds()
        await notify_user(message)
        logger.info(f"Funds check result: {message}")
        if not has_funds:
            await notify_user("Orders will not be placed tomorrow due to insufficient funds. 🌝")
            logger.warning("Insufficient funds for placing orders tomorrow.")
    except Exception as e:
        logger.error(f"Error checking funds: {e}")


async def on_order_filled():
    """Callback function when an order is filled."""
    try:
        await notify_user("An order was filled! Checking available funds... 🌚")
        logger.info("Order filled notification sent.")
        await check_funds_and_notify()
    except Exception as e:
        logger.error(f"Error handling order filled callback: {e}")


async def start_order_monitoring(order_ids):
    """Start monitoring filled orders after placing them."""
    try:
        await notify_user("Orders placed! Starting to monitor for filled orders... 🌚")
        logger.info("Order monitoring started.")
        await monitor_filled_orders(order_ids, on_order_filled)
    except Exception as e:
        logger.error(f"Error starting order monitoring: {e}")


async def place_orders_and_monitor():
    """Place orders and start monitoring."""
    try:
        order_ids = place_orders()
        logger.info(f"Orders placed with IDs: {order_ids}")
        await start_order_monitoring(order_ids)
    except Exception as e:
        logger.error(f"Error placing orders and starting monitoring: {e}")


async def cancel_orders_and_notify():
    """Cancel all orders and notify."""
    try:
        message = cancel_orders()
        await notify_user(message)
        logger.info(f"Orders canceled notification sent: {message}")
    except Exception as e:
        logger.error(f"Error canceling orders: {e}")


def daily_schedule():
    scheduler = AsyncIOScheduler()

    # Place orders at 00:15 AM UTC
    scheduler.add_job(
        place_orders_and_monitor,
        "cron",
        hour=0,
        minute=15,
        timezone="UTC",
    )

    # 30 minutes of black-out period between 23:45 PM and 00:15 AM the next day

    # Cancel orders at 23:45 PM UTC
    scheduler.add_job(
        cancel_orders_and_notify,
        "cron",
        hour=23,
        minute=45,
        timezone="UTC",
    )

    scheduler.start()
    logger.info("Scheduler started.")


if __name__ == "__main__":
    try:
        asyncio.run(notify_user("Trading bot started! 🌚"))
        logger.info("Bot started notification sent.")
        daily_schedule()

        # Start the asyncio event loop to keep the scheduler running
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        logger.error(f"Error running the scheduler: {e}")