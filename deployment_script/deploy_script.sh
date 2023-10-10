#!/bin/bash

# STEP 1 - Kill existing process running on the application port
PORT_NUMBER=$1
LOG_ENV=$2
ADDRESS=$3
echo "Port number is $PORT_NUMBER"
echo "environment is $LOG_ENV"
echo "address is $ADDRESS"


cd src
pwd
python -V
export PYTHONPATH=${PYTHONPATH}:$PWD


ray start --head

python main.py --http-port $PORT_NUMBER --http-address $ADDRESS