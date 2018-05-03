#!/bin/bash
set -e # exit immediately

cd /home/ubuntu/arb
    source /home/ubuntu/arb/conf_credentialed/env_prod

trap 'kill -TERM $PID' TERM INT

# main program
/usr/bin/python wsgi.py

#uwsgi --http 0.0.0.0:5000 --enable-threads --module wsgi

PID=$!
wait $PID
trap - TERM INT
wait $PID
EXIT_STATUS=$?
