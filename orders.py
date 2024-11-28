import ccxt
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv()

UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")

# Load min and max dips from the environment
MIN_PERCENTAGE_DIP = int(os.getenv("MIN_PERCENTAGE_DIP", 1))
MAX_PERCENTAGE_DIP = int(os.getenv("MAX_PERCENTAGE_DIP", 15))

exchange = ccxt.upbit({
    "apiKey": UPBIT_ACCESS_KEY,
    "secret": UPBIT_SECRET_KEY,
})


def get_open_price():
    """Fetch the open price of BTC/KRW."""
    ticker = exchange.fetch_ticker("BTC/KRW")
    return ticker["open"]


def get_krw_balance():
    """Fetch available KRW balance."""
    balance = exchange.fetch_balance()
    return balance["KRW"]["free"]


def calculate_required_funds():
    """Calculate the total KRW required for the orders."""
    amounts = range(6000, 6000 + (MAX_PERCENTAGE_DIP - MIN_PERCENTAGE_DIP + 1) * 1000, 1000)
    return sum(amounts)


def check_funds():
    """Check if there are enough funds to place the next day's orders."""
    available = get_krw_balance()
    required = calculate_required_funds()
    if available >= required:
        return True, f"Sufficient funds: {available} KRW available for {required} KRW required."
    else:
        return False, f"Insufficient funds: {available} KRW available, but {required} KRW required."


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
            orders.append(order["id"])  # Keep track of the order IDs
        return orders  # Return order IDs for monitoring
    except Exception as e:
        return f"Error placing orders: {e}"


def cancel_orders():
    """Cancel all open BTC/KRW orders."""
    try:
        open_orders = exchange.fetch_open_orders("BTC/KRW")
        for order in open_orders:
            exchange.cancel_order(order["id"])
        return "Canceled all orders successfully."
    except Exception as e:
        return f"Error canceling orders: {e}"


def monitor_filled_orders(order_ids, on_filled_callback):
    """
    Monitor the status of placed orders.

    Args:
        order_ids (list): List of order IDs to monitor.
        on_filled_callback (function): Function to call when an order is filled.
    """
    try:
        while order_ids:
            for order_id in order_ids[:]:  # Copy the list to avoid modification issues
                order = exchange.fetch_order(order_id, "BTC/KRW")
                if order["status"] == "closed":  # Order is filled
                    order_ids.remove(order_id)  # Remove the filled order from the list
                    on_filled_callback()  # Trigger the callback
            sleep(10)  # Wait 10 seconds before checking again
    except Exception as e:
        print(f"Error monitoring orders: {e}")
