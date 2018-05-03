#!/bin/bash
set -e # exit immediately

# Directory
cd /home/ubuntu/arb

# Environment variables
cat /home/ubuntu/arb/conf_credentialed/env-mock_trade-01
source /home/ubuntu/arb/conf_credentialed/env-mock_trade-01

trap 'kill -TERM $PID' TERM INT

# Task
/usr/bin/python -m arb.app.tasks.mock_live

# Cleanup
PID=$!
wait $PID
trap - TERM INT
wait $PID
EXIT_STATUS=$?
