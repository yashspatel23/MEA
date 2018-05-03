#!/bin/bash
set -e # exit immediately

# Directory
cd /home/ubuntu/arb

# Environment variables
source /home/ubuntu/arb/conf_credentialed/env-basic

trap 'kill -TERM $PID' TERM INT

# Task
/usr/bin/python -m arb.app.tasks.data_collection

# Cleanup
PID=$!
wait $PID
trap - TERM INT
wait $PID
EXIT_STATUS=$?
