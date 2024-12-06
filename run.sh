#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Run the bot in the background and log output to bot.log
nohup python bot.py > bot.log 2>&1 &

# Optionally, you can print the PID of the background process
echo "Bot is running in the background with PID: $!"