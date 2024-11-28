from apscheduler.schedulers.background import BackgroundScheduler
from orders import place_orders, cancel_orders, check_funds, monitor_filled_orders
from telegram import Bot
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)


async def notify_user(message):
    """Send a message to the user via Telegram."""
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Error notifying user: {e}")


async def check_funds_and_notify():
    """Check if sufficient funds are available and notify the user."""
    has_funds, message = check_funds()
    await notify_user(message)
    if not has_funds:
        await notify_user("Orders will not be placed tomorrow due to insufficient funds. 🌚")


async def on_order_filled():
    """Callback function when an order is filled."""
    await notify_user("An order was filled! Checking available funds... 🌝")
    await check_funds_and_notify()


def daily_schedule():
    scheduler = BackgroundScheduler()

    # Place orders at 00:05 AM UTC
    scheduler.add_job(
        lambda: asyncio.run(start_order_monitoring(place_orders())), "cron", hour=0, minute=5, timezone="UTC"
    )

    # Cancel orders at 23:55 PM UTC
    scheduler.add_job(
        lambda: asyncio.run(notify_user(cancel_orders())), "cron", hour=23, minute=55, timezone="UTC"
    )

    scheduler.start()


async def start_order_monitoring(order_ids):
    """Start monitoring filled orders after placing them."""
    await notify_user("Orders placed! Starting to monitor for filled orders... 🌝")
    monitor_filled_orders(order_ids, lambda: asyncio.run(on_order_filled()))


if __name__ == "__main__":
    asyncio.run(notify_user("Trading bot started! 🌚"))
    daily_schedule()
    while True:
        pass
