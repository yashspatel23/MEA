#!/bin/bash
set -e # exit immediately

# Directory
cd /home/ubuntu/arb

# Environment variables
source /home/ubuntu/arb/conf_credentialed/sensitive_env-live_trade-01

trap 'kill -TERM $PID' TERM INT

# Task
/usr/bin/python -m arb.app.tasks.live_trade_01

# Cleanup
PID=$!
wait $PID
trap - TERM INT
wait $PID
EXIT_STATUS=$?
