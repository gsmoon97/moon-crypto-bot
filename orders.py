# orders.py
import ccxt
import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from asyncio import sleep

# Load environment variables
load_dotenv()

UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
MIN_PERCENTAGE_DIP = int(os.getenv("MIN_PERCENTAGE_DIP", 1))
MAX_PERCENTAGE_DIP = int(os.getenv("MAX_PERCENTAGE_DIP", 10))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s",
    handlers=[
        logging.FileHandler("orders.log"),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger(__name__)

# Initialize the exchange
exchange = ccxt.upbit({
    "apiKey": UPBIT_ACCESS_KEY,
    "secret": UPBIT_SECRET_KEY,
})


def get_open_price():
    try:
        ticker = exchange.fetch_ticker("BTC/KRW")
        open_price = ticker["open"]
        logger.info(f"Fetched open price: {open_price} KRW")
        return open_price
    except Exception as e:
        logger.error(f"Error fetching open price: {e}")
        raise


def get_krw_balance():
    """
    Fetch the KRW balance, including funds reserved for open orders.
    """
    try:
        # Fetch total KRW balance
        balance = exchange.fetch_balance()
        available_balance = balance["KRW"]["free"]

        # Fetch open orders and calculate reserved funds
        open_orders = exchange.fetch_open_orders("BTC/KRW")
        reserved_balance = 0
        for order in open_orders:
            reserved_balance += order["price"] * order["amount"]

        # Add reserved funds to available balance
        total_balance = available_balance + reserved_balance
        logger.info(
            f"Available balance: {available_balance} KRW, "
            f"Reserved balance: {reserved_balance} KRW, "
            f"Total usable balance: {total_balance} KRW"
        )
        return total_balance
    except Exception as e:
        logger.error(f"Error fetching KRW balance: {e}")
        raise


def calculate_required_funds():
    try:
        amounts = range(6000, 6000 + (MAX_PERCENTAGE_DIP - MIN_PERCENTAGE_DIP + 1) * 1000, 1000)
        required_funds = sum(amounts)
        logger.info(f"Calculated required funds: {required_funds} KRW")
        return required_funds
    except Exception as e:
        logger.error(f"Error calculating required funds: {e}")
        raise


def check_funds():
    """
    Check if sufficient funds are available for placing orders.
    """
    try:
        available = get_krw_balance()
        required = calculate_required_funds()
        if available >= required:
            logger.info(
                f"Sufficient funds: {available} KRW available for {required} KRW required."
            )
            return True, f"Sufficient funds: {available} KRW available for {required} KRW required. 🌚"
        else:
            logger.warning(
                f"Insufficient funds: {available} KRW available, but {required} KRW required."
            )
            return False, f"Insufficient funds: {available} KRW available, but {required} KRW required. 🌝"
    except Exception as e:
        logger.error(f"Error checking funds: {e}")
        raise


def place_orders():
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
        return ", ".join(orders)  # Format order IDs into a string
    except Exception as e:
        logger.error(f"Error placing orders: {e}")
        raise


def fetch_filled_orders():
    """
    Fetch all filled BTC/KRW orders for the day.
    """
    try:
        all_orders = exchange.fetch_orders("BTC/KRW")
        today = datetime.now().date()
        filled_orders = [
            order for order in all_orders
            if order["status"] == "closed" and
            datetime.fromtimestamp(order["timestamp"] / 1000, tz=timezone.utc).date() == today
        ]
        return filled_orders
    except Exception as e:
        logger.error(f"Error fetching filled orders: {e}")
        raise


def calculate_btc_and_avg_price():
    """
    Calculate the total BTC purchased and the average purchase price for the day.
    """
    try:
        filled_orders = fetch_filled_orders()
        total_btc = sum(order["amount"] for order in filled_orders)
        total_cost = sum(order["amount"] * order["price"] for order in filled_orders)
        avg_price = total_cost / total_btc if total_btc > 0 else 0

        logger.info(
            f"Total BTC purchased today: {total_btc}, Average price: {avg_price} KRW"
        )
        return total_btc, avg_price
    except Exception as e:
        logger.error(f"Error calculating BTC and average price: {e}")
        raise


def get_btc_balance():
    """
    Fetch the total BTC balance in the account.
    """
    try:
        balance = exchange.fetch_balance()
        btc_balance = balance["BTC"]["free"]
        logger.info(f"Current BTC balance: {btc_balance} BTC")
        return btc_balance
    except Exception as e:
        logger.error(f"Error fetching BTC balance: {e}")
        raise


def cancel_orders():
    """
    Cancel all open BTC/KRW orders and calculate daily BTC purchase summary.
    """
    try:
        # Cancel all open orders
        open_orders = exchange.fetch_open_orders("BTC/KRW")
        if not open_orders:
            logger.info("No open orders to cancel.")
            return "No open orders to cancel. 🌝"
        
        for order in open_orders:
            exchange.cancel_order(order["id"])
            logger.info(f"Canceled order: {order['id']}")
        
        # Calculate BTC purchased today and average price
        total_btc, avg_price = calculate_btc_and_avg_price()

        # Fetch current BTC balance
        btc_balance = get_btc_balance()

        # Prepare summary message
        summary = (
            f"Orders canceled successfully. 🌚\n"
            f"Today's BTC purchases: {total_btc:.6f} BTC at an average price of {avg_price:.2f} KRW.\n"
            f"Current BTC holdings: {btc_balance:.6f} BTC."
        )
        logger.info(summary)
        return summary
    except Exception as e:
        logger.error(f"Error canceling orders: {e}")
        raise


async def monitor_filled_orders(order_ids, on_filled_callback):
    try:
        logger.info("Started monitoring filled orders.")
        while order_ids:
            for order_id in order_ids[:]:
                order = exchange.fetch_order(order_id, "BTC/KRW")
                if order["status"] == "closed":
                    order_ids.remove(order_id)
                    logger.info(f"Order filled: {order_id}")
                    await on_filled_callback()  # Use await to ensure the callback is run asynchronously
            await sleep(60)  # Use asyncio.sleep to avoid blocking the event loop
        logger.info("Stopped monitoring filled orders.")
    except Exception as e:
        logger.error(f"Error monitoring filled orders: {e}")