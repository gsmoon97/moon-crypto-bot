import ccxt
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import numpy as np
import os
import sqlite3

# Load environment variables
load_dotenv()

UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
ORDER_TRACKER_DB = "order_tracker.db"

# Configure logging
log_file = "exchange_bot.log"
log_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[log_handler]
)
logger = logging.getLogger(__name__)

# Initialize Upbit
upbit = ccxt.upbit({
    'apiKey': UPBIT_ACCESS_KEY,
    'secret': UPBIT_SECRET_KEY,
})

# Initialize Flask app
app = Flask(__name__)

# ---------------- Database Functions ----------------
def initialize_db():
    """Initialize the order_tracker database."""
    conn = sqlite3.connect(ORDER_TRACKER_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            percentage_dip REAL,
            price REAL,
            amount REAL,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_order(order_id, percentage_dip, price, amount, created_at):
    """Insert a new order into the database."""
    conn = sqlite3.connect(ORDER_TRACKER_DB)
    c = conn.cursor()
    c.execute('''
        INSERT INTO orders (id, percentage_dip, price, amount, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (order_id, percentage_dip, price, amount, created_at))
    conn.commit()
    conn.close()
    logger.info(f"Inserted new order {order_id} into the database.")

def delete_order(order_id):
    """Delete an order from the database."""
    conn = sqlite3.connect(ORDER_TRACKER_DB)
    c = conn.cursor()
    c.execute('''DELETE FROM orders WHERE id = ?''', (order_id,))
    conn.commit()
    conn.close()
    logger.info(f"Deleted order {order_id} from the database.")

def get_order_by_id(order_id):
    """Retrieve an order by id."""
    conn = sqlite3.connect(ORDER_TRACKER_DB)
    c = conn.cursor()
    c.execute('''SELECT * FROM orders WHERE id = ?''', (order_id,))
    row = c.fetchone()
    conn.close()
    # Convert each row into a dictionary
    keys = ["id", "percentage_dip", "price", "amount"]
    return [dict(zip(keys, row[:4]))]

def get_orders():
    """Retrieve all orders."""
    conn = sqlite3.connect(ORDER_TRACKER_DB)
    c = conn.cursor()
    c.execute('''SELECT * FROM orders''')
    rows = c.fetchall()
    conn.close()
    # Convert each row into a dictionary
    keys = ["id", "percentage_dip", "price", "amount"]
    return [dict(zip(keys, row[:4])) for row in rows]

# ---------------- Helper Functions ----------------
def get_open_price():
    """Retrieve open price from exchange."""
    try:
        ticker = upbit.fetch_ticker("BTC/KRW")
        return float(ticker["open"])
    except Exception as e:
        logger.error(f"Error fetching open price: {e}")
        return None

# ---------------- REST API Endpoints ----------------
@app.route("/health", methods=["GET"])
def health_check():
    try:
        return jsonify({"status": "OK", "message": "The Flask app is running properly."}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "ERROR", "message": "Health check failed."}), 500

@app.route('/check_balances', methods=['GET'])
def check_balances():
    try:
        # Fetch balances from Upbit
        balance = upbit.fetch_balance()
        non_zero_balances = {
            asset: amount for asset, amount in balance.get('total', {}).items() if amount > 0
        }
        return jsonify({"non_zero_balances": non_zero_balances})
    except Exception as e:
        logger.error(f"Error fetching balances: {e}")
        return jsonify({"error": "Failed to fetch balances"}), 500

@app.route("/place_orders", methods=["POST"])
def place_orders():
    try:
        open_price = get_open_price()
        data = request.json
        start_percentage_dip = data.get("start_percentage_dip")
        end_percentage_dip = data.get("end_percentage_dip")
        percentage_dip_increment = data.get("percentage_dip_increment")
        start_amount = data.get("start_amount")
        amount_increment = data.get("amount_increment")

        if None in (start_percentage_dip, end_percentage_dip, percentage_dip_increment, start_amount, amount_increment):
            return jsonify({"error": "Missing required parameters."}), 400
        
        placed_orders = []
        for percentage_dip in np.arange(start_percentage_dip, end_percentage_dip + percentage_dip_increment, percentage_dip_increment):
            try:
                price = round(open_price * (1 - percentage_dip / 100), -3)  # Round to the nearest thousands to comply with the exchange requirments
                amount = (start_amount + (percentage_dip - start_percentage_dip) * amount_increment) / price
                order = upbit.create_limit_buy_order("BTC/KRW", amount, price)
                insert_order(order['id'], percentage_dip, order['price'], order['amount'], order['timestamp'])  # Save the order to the database
                logger.info(f"Placed order: {order['id']} - {percentage_dip}% dip.")
                placed_orders.append({
                    "order_id": order['id'], 
                    "percentage_dip": percentage_dip, 
                    "price": order['price'], 
                    "amount": order['amount']
                })
                # time.sleep(1)  # Add a small delay between consecutive orders to comply with API rate limits
            except Exception as e:
                logger.error(f"Failed to place order for {percentage_dip}% dip: {e}")
        return jsonify({"placed_orders": placed_orders})
    except Exception as e:
        logger.error(f"Error placing orders: {e}")
        return jsonify({"error": "Failed to place orders"}), 500

@app.route("/cancel_orders", methods=["POST"])
def cancel_orders():
    try:
        open_orders_from_exchange = upbit.fetch_open_orders("BTC/KRW")  # might include other open orders not placed by the bot
        open_order_ids_from_exchange = [order['id'] for order in open_orders_from_exchange]
        orders_from_db = get_orders()
        open_orders_from_db = [order for order in orders_from_db if order['id'] in open_order_ids_from_exchange]  # filter only the open orders placed by the bot
        filled_orders_from_db = [order for order in orders_from_db if order['id'] not in open_order_ids_from_exchange]  # filter only the filled orders placed by the bot

        cancelled_orders = []
        for open_order in open_orders_from_db:
            try:
                order_id = open_order['id']
                upbit.cancel_order(order_id)
                delete_order(order_id)
                logger.info(f"Cancelled order '{order_id}'")
                cancelled_orders.append({
                    "order_id": order_id, 
                    "percentage_dip": open_order['percentage_dip'], 
                    "price": open_order['price'], 
                    "amount": open_order['amount']
                })
                # time.sleep(1)  # Add a small delay between consecutive orders to comply with API rate limits
            except Exception as e:
                logger.error(f"Failed to cancel order '{order_id}': {e}")

        filled_orders = []
        for filled_order in filled_orders_from_db:
            try:
                order_id = filled_order['id']
                delete_order(order_id)
                filled_orders.append({
                    "order_id": order_id, 
                    "percentage_dip": filled_order['percentage_dip'], 
                    "price": filled_order['price'], 
                    "amount": filled_order['amount']
                })
            except Exception as e:
                logger.error(f"Failed to process order '{order_id}': {e}")
        
        return jsonify({"cancelled_orders": cancelled_orders, "filled_orders": filled_orders})
    except Exception as e:
        logger.error(f"Error cancelling orders: {e}")
        return jsonify({"error": "Failed to cancel orders"}), 500
    
@app.route("/check_orders", methods=["GET"])
def check_orders():
    try:
        open_orders_from_exchange = upbit.fetch_open_orders("BTC/KRW")  # might include other open orders not placed by the bot
        open_order_ids_from_exchange = [order['id'] for order in open_orders_from_exchange]
        orders_from_db = get_orders()
        open_orders_from_db = [order for order in orders_from_db if order['id'] in open_order_ids_from_exchange]  # filter only the open orders placed by the bot
        open_orders = [{"order_id": open_order['id'], "percentage_dip": open_order['percentage_dip'], "price": open_order['price'], "amount": open_order['amount']} for open_order in open_orders_from_db]
        
        return jsonify({"open_orders": open_orders})
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return jsonify({"error": "Failed to fetch orders"}), 500


# ---------------- Main Program ----------------
if __name__ == "__main__":
    initialize_db()
    logger.info("Exchange bot started with REST API.")
    app.run(host="0.0.0.0", port=5000, debug=True)
