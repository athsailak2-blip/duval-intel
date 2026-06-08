#!/bin/bash
# Duval County Lead Intelligence - Daily Refresh
# Add to crontab: 0 6 * * * /path/to/scripts/run_refresh.sh

cd "$(dirname "$0")/.."

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: Python 3 not found"
    exit 1
fi

# Run refresh
python3 scripts/daily_refresh.py

if [ $? -eq 0 ]; then
    echo "Refresh completed successfully"
else
    echo "Refresh completed with errors"
    exit 1
fi
