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
ALICE_ID=$(curl -s -X POST "http://127.0.0.1:8000/traders" -H "Content-Type: application/json" -d '{"username": "alice"}' | jq -r '.trader_id')
BOB_ID=$(curl -s -X POST "http://127.0.0.1:8000/traders" -H "Content-Type: application/json" -d '{"username": "bob"}' | jq -r '.trader_id')
CHARLIE_ID=$(curl -s -X POST "http://127.0.0.1:8000/traders" -H "Content-Type: application/json" -d '{"username": "charlie"}' | jq -r '.trader_id')
DAVID_ID=$(curl -s -X POST "http://127.0.0.1:8000/traders" -H "Content-Type: application/json" -d '{"username": "david"}' | jq -r '.trader_id')

echo "Registered Alice with ID: $ALICE_ID"
echo "Registered Bob with ID: $BOB_ID"
echo "Registered Charlie with ID: $CHARLIE_ID"
echo "Registered David with ID: $DAVID_ID"

print_message "Building the Order Book"

# Alice places a buy order
curl -X POST "http://127.0.0.1:8000/orders" -H "Content-Type: application/json" -d '{"trader_id": "'"$ALICE_ID"'", "side": "buy", "price": 100.0, "quantity": 10, "priority": 1}' | jq

# Bob places a sell order
curl -X POST "http://127.0.0.1:8000/orders" -H "Content-Type: application/json" -d '{"trader_id": "'"$BOB_ID"'", "side": "sell", "price": 102.0, "quantity": 5, "priority": 1}' | jq

# Charlie places another buy order
curl -X POST "http://127.0.0.1:8000/orders" -H "Content-Type: application/json" -d '{"trader_id": "'"$CHARLIE_ID"'", "side": "buy", "price": 101.0, "quantity": 8, "priority": 1}' | jq

print_message "Current Order Book"
curl -s http://127.0.0.1:8000/orderbook | jq

print_message "David places a sell order that matches Charlie's buy order"
# This will match Charlie's buy order at 101.0 and fill it completely.
curl -X POST "http://127.0.0.1:8000/orders" \
-H "Content-Type: application/json" \
-d '{
  "trader_id": "'"$DAVID_ID"'",
  "side": "sell",
  "price": 101.0,
  "quantity": 8,
  "priority": 1
}' | jq

print_message "Order Book after David's sell order"
curl -s http://127.0.0.1:8000/orderbook | jq

print_message "Verifying Database Records"

echo "--- All Traders ---"
curl -s http://127.0.0.1:8000/traders | jq

echo "--- All Orders ---"
curl -s http://127.0.0.1:8000/orders | jq

echo "--- All Trades ---"
curl -s http://127.0.0.1:8000/trades | jq

print_message "Final Trader Balances"
echo "Alice's Account:"
curl -s "http://127.0.0.1:8000/traders/$ALICE_ID" | jq
echo "Bob's Account:"
curl -s "http://127.0.0.1:8000/traders/$BOB_ID" | jq
echo "Charlie's Account:"
curl -s "http://127.0.0.1:8000/traders/$CHARLIE_ID" | jq
echo "David's Account:"
curl -s "http://127.0.0.1:8000/traders/$DAVID_ID" | jq

echo ""