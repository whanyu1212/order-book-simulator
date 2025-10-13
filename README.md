<!-- omit in toc -->
# 📈 Order Book Simulator
This repository contains proof-of-concept implementation of an Order Book Simulator in Python.

---

<!-- omit in toc -->
## 📜 Table of Content

- [📖 Overview](#-overview)
- [🚀 Getting Started](#-getting-started)
- [🧩 Components](#-components)
- [🚀 Running the API and Trade Simulation](#-running-the-api-and-trade-simulation)
- [📚 API Documentation (Swagger UI)](#-api-documentation-swagger-ui)
- [🏃‍♀️ Running the Legacy Simulation](#️-running-the-legacy-simulation)
- [📝 Learning Notes](#-learning-notes)
  - [Financial Computing Best Practices](#financial-computing-best-practices)
    - [Using Decimal Instead of Float for Financial Calculations](#using-decimal-instead-of-float-for-financial-calculations)

### 📖 Overview
This project is a proof-of-concept implementation of an order book simulator, focusing on limit orders. It simulates the core functionalities of a financial market order book, including adding and canceling buy and sell limit orders. It also provides a FastAPI interface to interact with the order book.

---

### 🚀 Getting Started
This repository uses `Poetry` for dependency management.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/whanyu1212/order-book-simulator.git
   cd order-book-simulator
   ```
   
2. **Install dependencies:**
   Make sure you have Poetry installed. Then, run the following command to install the project dependencies:
   ```bash
   poetry install
   ```

3. **Activate the virtual environment:**
   To activate the virtual environment managed by Poetry, run:
   ```bash
   poetry config virtualenvs.in-project true
   source .venv/bin/activate
   ```

4. **Set up Jupyter Kernel:**
   To use this environment within Jupyter, install a new kernel:
   ```bash
   python -m ipykernel install --user --name=order-book-simulator
   ```
---

### 🧩 Components
This simulator is built around a few core components, each with a specific responsibility. The main components are organized into the following modules:

- **`config`**: This module contains the data structures for the application, including `OrderRequest`, `Trade`, and `Account`. These data classes are defined using Pydantic for data validation and serialization.

- **`core`**: This module contains the main business logic of the order book simulator. It includes:
  - `OrderBook`: Manages the collections of buy (bids) and sell (asks) orders. It uses `SortedDict` for efficient sorting and matching.
  - `MatchingEngine`: Responsible for matching buy and sell orders. It takes an `OrderRequest` and tries to match it against existing orders in the `OrderBook`.
  - `TraderAccountManager`: Manages trader accounts, including balances and registration.

- **`database`**: This module handles all database interactions. It includes:
  - `models`: Defines the database schema for orders, trades, and trader accounts.
  - `session`: Manages database sessions and connections.

- **`api`**: This module exposes the functionality of the simulator through a FastAPI web server. It defines the API endpoints for creating traders, submitting orders, and retrieving order book data.

- **`websocket`**: This module provides real-time communication capabilities. It includes:
  - `ConnectionManager`: Manages active WebSocket connections and broadcasts trade updates to all connected clients.

- **`analysis`**: This module provides tools for analyzing the order book and trading activity. It includes:
  - `MetricsCalculator`: Calculates various metrics, such as bid-ask spread and market depth.

### 🚀 Running the API and Trade Simulation
The primary way to interact with the simulator is through the FastAPI web server. Helper scripts are provided in the `scripts` directory.

1.  **Make Scripts Executable:**
    Before running the scripts for the first time, you need to give them execute permissions.
    ```bash
    chmod +x scripts/run.sh
    chmod +x scripts/simulate.sh
    chmod +x scripts/listen_trades.py
    ```

2.  **Start the Server (Terminal 1):**
    Open a terminal and run the following script to start the Uvicorn server.
    ```bash
    ./scripts/run.sh
    ```
    The server will be running on `http://127.0.0.1:8000`. Leave this terminal running.

3.  **Listen for Trades (Terminal 2):**
    Open a **second terminal** and run the `listen_trades.py` script. This script connects to the WebSocket endpoint and will print any trades that occur in real-time.
    ```bash
    python scripts/listen_trades.py
    ```
    Keep this terminal visible so you can see the trade notifications.

4.  **Run the Simulation Script (Terminal 3):**
    Open a **third terminal** and run the simulation script. This script uses `curl` to send HTTP requests to the server, which will trigger trades.
    > **What is `curl`?** `curl` (Client for URL) is a command-line tool used to transfer data to or from a server. It's a powerful way to interact with and test APIs directly from the terminal.
    ```bash
    ./scripts/simulate.sh
    ```
    As soon as you run this, you will see the trade appear in the second terminal (the one running `listen_trades.py`).

---

### 📚 API Documentation (Swagger UI)
One of the key advantages of FastAPI is its automatically generated interactive documentation.

Once the server is running (using `./scripts/run.sh`), you can access the Swagger UI by opening your web browser and navigating to:

[**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)

This page allows you to:
-   Visualize all the API endpoints.
-   See the expected request and response models.
-   Interact with the API directly from your browser.

---

### 🏃‍♀️ Running the Legacy Simulation
To see the original non-API components work together, you can run the example simulation script:
```bash
python -m examples.simulation
```

---

### 📝 Learning Notes

#### Financial Computing Best Practices

##### Using Decimal Instead of Float for Financial Calculations
In this project, we use Python's `Decimal` type instead of `float` for all monetary values and calculations. Here's why this is crucial for financial applications:

```python
# Processing 100,000 transactions with 1 cent fee each
small_fee = 0.01  # 1 cent fee
num_transactions = 100000

# Using float - accumulates errors
float_total = 0
for _ in range(num_transactions):
    float_total += small_fee

# Using Decimal - maintains precision
from decimal import Decimal
decimal_total = Decimal('0')
for _ in range(num_transactions):
    decimal_total += Decimal('0.01')

print(f"Float total fees: ${float_total}")         # 999.9999999999091
print(f"Decimal total fees: ${decimal_total}")     # 1000.00
print(f"Difference in cents: {(decimal_total - Decimal(str(float_total))) * 100}")
```

This example demonstrates why using `Decimal` is crucial in our order book simulator:
- Small rounding errors accumulate in float calculations
- With high-volume trading, these errors can become significant
- Financial calculations require exact precision, especially with money
- Even a fraction of a cent difference can matter when scaled up
- Regulatory compliance often requires exact decimal arithmetic

This precision is essential in our order book simulator because:
- We're handling monetary values
- Calculations need to be exact for trading
- Account balances must be precise
- Financial auditing requires exact arithmetic
- Multiple transactions should not lead to rounding errors

---

More learning notes will be added as we implement new features and encounter interesting technical concepts.
This will simulate a series of order requests and print out the resulting trades and the final state of the order book directly in your console.