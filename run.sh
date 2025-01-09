#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Run exchange_bot.py in the background
nohup python exchange_bot.py > exchange_bot.log 2>&1 &
EXCHANGE_BOT_PID=$!
echo "Exchange Bot is running with PID: $EXCHANGE_BOT_PID"

# Wait for the REST API from exchange_bot.py to become available
EXCHANGE_FLASK_URL="http://localhost:5000/health"  # endpoint for health check
echo "Waiting for Exchange Bot REST API to start..."
while ! curl --silent --output /dev/null "$EXCHANGE_FLASK_URL"; do
    sleep 2  # Wait for 2 seconds before checking again
done
echo "Exchange Bot REST API is up and running!"

# Run schedule_bot.py in the background
nohup python schedule_bot.py > schedule_bot.log 2>&1 &
SCHEDULE_BOT_PID=$!
echo "Schedule Bot is running with PID: $SCHEDULE_BOT_PID"

# Wait for the REST API from schedule_bot.py to become available
SCHEDULE_FLASK_URL="http://localhost:6000/health"  # endpoint for health check
echo "Waiting for Schedule Bot REST API to start..."
while ! curl --silent --output /dev/null "$SCHEDULE_FLASK_URL"; do
    sleep 2  # Wait for 2 seconds before checking again
done
echo "Schedule Bot REST API is up and running!"

# Run telegram_bot.py in the background
nohup python telegram_bot.py > telegram_bot.log 2>&1 &
TELEGRAM_BOT_PID=$!
echo "Telegram Bot is running with PID: $TELEGRAM_BOT_PID"

# Optional: Print all PIDs
echo "All bots are running:"
echo " - Exchange Bot PID: $EXCHANGE_BOT_PID"
echo " - Schedule Bot PID: $SCHEDULE_BOT_PID"
echo " - Telegram Bot PID: $TELEGRAM_BOT_PID"

