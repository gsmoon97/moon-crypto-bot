import ccxt
import os
import logging
from dotenv import load_dotenv
from time import sleep

# Load environment variables
load_dotenv()

UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
MIN_PERCENTAGE_DIP = int(os.getenv("MIN_PERCENTAGE_DIP", 1))
MAX_PERCENTAGE_DIP = int(os.getenv("MAX_PERCENTAGE_DIP", 15))

# Configure logging
logging.basicConfig(
    filename="orders.log",  # Log to a file named orders.log
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize the exchange
exchange = ccxt.upbit({
    "apiKey": UPBIT_ACCESS_KEY,
    "secret": UPBIT_SECRET_KEY,
})


def get_open_price():
    """Fetch the open price of BTC/KRW."""
    try:
        ticker = exchange.fetch_ticker("BTC/KRW")
        open_price = ticker["open"]
        logger.info(f"Fetched open price: {open_price} KRW")
        return open_price
    except Exception as e:
        logger.error(f"Error fetching open price: {e}")
        raise


def get_krw_balance():
    """Fetch available KRW balance."""
    try:
        balance = exchange.fetch_balance()
        available_balance = balance["KRW"]["free"]
        logger.info(f"Fetched KRW balance: {available_balance} KRW")
        return available_balance
    except Exception as e:
        logger.error(f"Error fetching KRW balance: {e}")
        raise


def calculate_required_funds():
    """Calculate the total KRW required for the orders."""
    try:
        amounts = range(
            6000, 
            6000 + (MAX_PERCENTAGE_DIP - MIN_PERCENTAGE_DIP + 1) * 1000, 
            1000
        )
        required_funds = sum(amounts)
        logger.info(f"Calculated required funds: {required_funds} KRW")
        return required_funds
    except Exception as e:
        logger.error(f"Error calculating required funds: {e}")
        raise


def check_funds():
    """Check if there are enough funds to place the next day's orders."""
    try:
        available = get_krw_balance()
        required = calculate_required_funds()
        if available >= required:
            logger.info(f"Sufficient funds: {available} KRW available for {required} KRW required.")
            return True, f"Sufficient funds: {available} KRW available for {required} KRW required."
        else:
            logger.warning(f"Insufficient funds: {available} KRW available, but {required} KRW required.")
            return False, f"Insufficient funds: {available} KRW available, but {required} KRW required."
    except Exception as e:
        logger.error(f"Error checking funds: {e}")
        raise


def place_orders():
    """Place BTC/KRW orders."""
    try:
        open_price = get_open_price()
        orders = []

        for percentage_dip, krw in enumerate(
            range(6000, 6000 + (MAX_PERCENTAGE_DIP - MIN_PERCENTAGE_DIP + 1) * 1000, 1000),
            start=MIN_PERCENTAGE_DIP
        ):
            price = open_price * (1 - percentage_dip / 100)
            amount = krw / price
            order = exchange.create_limit_buy_order("BTC/KRW", amount, price)
            orders.append(order["id"])
            logger.info(f"Placed order: {order['id']} | Price: {price} | Amount: {amount} BTC")
        
        logger.info("All orders placed successfully.")
        return orders
    except Exception as e:
        logger.error(f"Error placing orders: {e}")
        raise


def cancel_orders():
    """Cancel all open BTC/KRW orders."""
    try:
        open_orders = exchange.fetch_open_orders("BTC/KRW")
        if not open_orders:
            logger.info("No open orders to cancel.")
            return "No open orders to cancel."
        
        for order in open_orders:
            exchange.cancel_order(order["id"])
            logger.info(f"Canceled order: {order['id']}")
        
        logger.info("Canceled all orders successfully.")
        return "Canceled all orders successfully."
    except Exception as e:
        logger.error(f"Error canceling orders: {e}")
        raise


def monitor_filled_orders(order_ids, on_filled_callback):
    """
    Monitor the status of placed orders.

    Args:
        order_ids (list): List of order IDs to monitor.
        on_filled_callback (function): Function to call when an order is filled.
    """
    try:
        logger.info("Started monitoring filled orders.")
        while order_ids:
            for order_id in order_ids[:]:
                order = exchange.fetch_order(order_id, "BTC/KRW")
                if order["status"] == "closed":  # Order is filled
                    order_ids.remove(order_id)
                    logger.info(f"Order filled: {order_id}")
                    on_filled_callback()  # Trigger the callback
            sleep(10)  # Wait 10 seconds before checking again
    except Exception as e:
        logger.error(f"Error monitoring orders: {e}")
        raise
