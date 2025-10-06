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
CHARLIE_ID=$(curl -s -X POST "http://127.0.0.1:8000/traders" -H "Content-Type: application/json" -d '{"username": "charlie"}' | tr -d '"')
DAVID_ID=$(curl -s -X POST "http://127.0.0.1:8000/traders" -H "Content-Type: application/json" -d '{"username": "david"}' | tr -d '"')

echo "Registered Alice with ID: $ALICE_ID"
echo "Registered Bob with ID: $BOB_ID"
echo "Registered Charlie with ID: $CHARLIE_ID"
echo "Registered David with ID: $DAVID_ID"

print_message "Building the Order Book"

# Alice places buy orders
curl -X POST "http://127.0.0.1:8000/orders" -H "Content-Type: application/json" -d '{"trader_id": "'"$ALICE_ID"'", "side": "buy", "price": 99.0, "quantity": 15, "priority": 1}' | jq
curl -X POST "http://127.0.0.1:8000/orders" -H "Content-Type: application/json" -d '{"trader_id": "'"$ALICE_ID"'", "side": "buy", "price": 98.0, "quantity": 20, "priority": 1}' | jq

# Bob places sell orders
curl -X POST "http://127.0.0.1:8000/orders" -H "Content-Type: application/json" -d '{"trader_id": "'"$BOB_ID"'", "side": "sell", "price": 101.0, "quantity": 10, "priority": 1}' | jq
curl -X POST "http://127.0.0.1:8000/orders" -H "Content-Type: application/json" -d '{"trader_id": "'"$BOB_ID"'", "side": "sell", "price": 102.0, "quantity": 5, "priority": 1}' | jq

# Charlie places a high-priority buy order
curl -X POST "http://127.0.0.1:8000/orders" -H "Content-Type: application/json" -d '{"trader_id": "'"$CHARLIE_ID"'", "side": "buy", "price": 99.0, "quantity": 5, "priority": 2}' | jq

print_message "Current Order Book"
curl -s http://127.0.0.1:8000/orderbook | jq

print_message "David places a large sell order that partially fills multiple buy orders"
# This will match Alice's and Charlie's orders at 99.0
curl -X POST "http://127.0.0.1:8000/orders" \
-H "Content-Type: application/json" \
-d '{
  "trader_id": "'"$DAVID_ID"'",
  "side": "sell",
  "price": 99.0,
  "quantity": 25,
  "priority": 1
}' | jq

print_message "Order Book after David's large sell"
curl -s http://127.0.0.1:8000/orderbook | jq

print_message "Alice places an aggressive buy order that crosses the spread"
# This will match Bob's sell order at 101.0
curl -X POST "http://127.0.0.1:8000/orders" \
-H "Content-Type: application/json" \
-d '{
  "trader_id": "'"$ALICE_ID"'",
  "side": "buy",
  "price": 101.5,
  "quantity": 10,
  "priority": 1
}' | jq

print_message "Final Order Book"
curl -s http://127.0.0.1:8000/orderbook | jq
echo ""