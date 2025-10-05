#!/bin/bash

# This script simulates interaction with the Order Book API.
# Make sure the server is running first by executing ./run.sh in another terminal.

# Function to print formatted messages
print_message() {
    echo ""
    echo "----------------------------------------"
    echo " $1"
    echo "----------------------------------------"
    echo ""
}

print_message "Registering Traders"
ALICE_ID=$(curl -s -X POST "http://127.0.0.1:8000/traders" -H "Content-Type: application/json" -d '{"username": "alice"}' | tr -d '"')
BOB_ID=$(curl -s -X POST "http://127.0.0.1:8000/traders" -H "Content-Type: application/json" -d '{"username": "bob"}' | tr -d '"')

echo "Registered Alice with ID: $ALICE_ID"
echo "Registered Bob with ID: $BOB_ID"

print_message "Submitting Initial Buy Order (Alice)"
curl -X POST "http://127.0.0.1:8000/orders" \
-H "Content-Type: application/json" \
-d '{
  "trader_id": "'"$ALICE_ID"'",
  "side": "buy",
  "price": 99.5,
  "quantity": 10,
  "priority": 1
}' | jq

print_message "Current Order Book"
curl -s http://127.0.0.1:8000/orderbook | jq

print_message "Submitting Matching Sell Order (Bob)"
# This order should match Alice's buy order
curl -X POST "http://127.0.0.1:8000/orders" \
-H "Content-Type: application/json" \
-d '{
  "trader_id": "'"$BOB_ID"'",
  "side": "sell",
  "price": 99.5,
  "quantity": 10,
  "priority": 1
}' | jq

print_message "Final Order Book"
curl -s http://127.0.0.1:8000/orderbook | jq
echo ""