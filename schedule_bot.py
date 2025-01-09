from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import os
import requests

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

EXCHANGE_API_URL = os.getenv("EXCHANGE_API_URL", "http://localhost:5000")  # REST API URL from exchange_bot.py

START_PERCENTAGE_DIP = float(os.getenv("START_PERCENTAGE_DIP", 1.0))
END_PERCENTAGE_DIP = float(os.getenv("END_PERCENTAGE_DIP", 10.0))
PERCENTAGE_DIP_INCREMENT = float(os.getenv("PERCENTAGE_DIP_INCREMENT", 1.0))
START_AMOUNT = int(os.getenv("START_AMOUNT", 6000))
AMOUNT_INCREMENT = int(os.getenv("AMOUNT_INCREMENT", 1000))

START_TIME = os.getenv("START_TIME", "00:05")
END_TIME = os.getenv("END_TIME", "23:55")

# Configure logging
log_file = "schedule_bot.log"
log_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG, 
    handlers=[log_handler]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
scheduler = BackgroundScheduler(timezone="UTC")

# ---------------- Helper Functions ----------------
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Check for HTTP errors
    except Exception as e:
        logger.error(f"Error sending a message: {e}")
        raise  # Re-raise the exception after logging

def place_orders():
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
            send_message(orders_message)
        else:
            send_message("No orders were placed 🌚")
    except Exception as e:
        logger.error(f"Error placing orders: {e}")
        send_message("An error occurred while placing orders. Please try again later 🌝")

def cancel_orders():
    try:
        response = requests.post(f"{EXCHANGE_API_URL}/cancel_orders")
        response.raise_for_status()  # Check for HTTP errors

        cancelled_orders = response.json().get('cancelled_orders', [])
        if cancelled_orders:
            orders_message = f"Cancelled {len(cancelled_orders)} orders:\n" + "\n".join(
                [f"- {cancelled_order['percentage_dip']:.2f}% Dip: {cancelled_order['amount']:,.8f} BTC @ {cancelled_order['price']:,.0f} KRW" for cancelled_order in cancelled_orders]
            )
            send_message(orders_message)
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
        send_message(stats_message)
    except Exception as e:
        logger.error(f"Error cancelling orders: {e}")
        send_message("An error occurred while cancelling orders. Please try again later 🌝")

def schedule_daily_jobs():
    """Schedules the place and cancel jobs based on START_TIME and END_TIME."""
    scheduler.add_job(place_orders, 'cron', hour=START_TIME.split(":")[0], minute=START_TIME.split(":")[1], id="place_orders_job")
    scheduler.add_job(cancel_orders, 'cron', hour=END_TIME.split(":")[0], minute=END_TIME.split(":")[1], id="cancel_orders_job")
    logger.info(f"Scheduled jobs: Place Orders at {START_TIME}, Cancel Orders at {END_TIME}")

# ---------------- REST API Endpoints ----------------
@app.route("/health", methods=["GET"])
def health_check():
    try:
        return jsonify({"status": "OK", "message": "The Flask app is running properly."}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "ERROR", "message": "Health check failed."}), 500

@app.route("/start_scheduler", methods=["POST"])
def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        schedule_daily_jobs()
        logger.info("Scheduler started and jobs scheduled.")
        return jsonify({"status": "Scheduler started and jobs scheduled."}), 200
    logger.warning("Scheduler already running.")
    return jsonify({"status": "Scheduler already running."}), 200

@app.route("/stop_scheduler", methods=["POST"])
def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
        return jsonify({"status": "Scheduler stopped."}), 200
    logger.warning("Scheduler is not running.")
    return jsonify({"status": "Scheduler is not running."}), 200


# ---------------- Main Program ----------------
if __name__ == "__main__":
    logger.info("Schedule bot started with REST API.")
    app.run(host="0.0.0.0", port=6000, debug=True)
