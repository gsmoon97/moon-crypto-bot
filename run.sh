#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Run exchange_bot.py in the background
nohup python exchange_bot.py > exchange_bot.log 2>&1 &
EXCHANGE_BOT_PID=$!
echo "Exchange Bot is running with PID: $EXCHANGE_BOT_PID"

# Wait for the REST API to become available
FLASK_URL="http://localhost:5000/health"  # endpoint for health check
echo "Waiting for REST API to start..."
while ! curl --silent --output /dev/null "$FLASK_URL"; do
    sleep 2  # Wait for 2 seconds before checking again
done
echo "REST API is up and running!"

# Run telegram_bot.py in the background
nohup python telegram_bot.py > telegram_bot.log 2>&1 &
TELEGRAM_BOT_PID=$!
echo "Telegram Bot is running with PID: $TELEGRAM_BOT_PID"

# Optional: Print both PIDs
echo "Both bots are running:"
echo " - Exchange Bot PID: $EXCHANGE_BOT_PID"
echo " - Telegram Bot PID: $TELEGRAM_BOT_PID"
