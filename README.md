<!-- omit in toc -->
# 📈 Order Book Simulator
This repository contains proof-of-concept implementation of an Order Book Simulator in Python.

---

<!-- omit in toc -->
## 📜 Table of Content

- [📖 Overview](#-overview)
- [🚀 Getting Started](#-getting-started)
- [🧩 Components](#-components)
- [🏃‍♀️ Running the Simulation](#️-running-the-simulation)

### 📖 Overview
This project is a proof-of-concept implementation of an order book simulator, focusing on limit orders. It simulates the core functionalities of a financial market order book, including adding and canceling buy and sell limit orders.

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
This simulator is built around a few core components: `OrderRequest`, `OrderBook`, `Trade`, and `MatchingEngine`.

- **`OrderRequest`**: This is a data class (using Pydantic) that represents a single order submitted to the book. It contains all the necessary information for an order, such as:
  - `order_id`: A unique identifier for the order.
  - `trader_id`: The identifier of the trader placing the order.
  - `side`: Whether the order is a `BUY` or `SELL`.
  - `price`: The price at which the trader is willing to buy or sell.
  - `quantity`: The amount of the asset to be traded.
  - `timestamp`: The time the order was created.

- **`OrderBook`**: This class is the heart of the simulator. It manages the collections of buy (bids) and sell (asks) orders.
  - It uses `SortedDict` from the `sortedcontainers` library to efficiently store and sort orders by price.
  - Bids are sorted from highest to lowest price, while asks are sorted from lowest to highest.
  - It provides methods to add new orders, cancel existing ones, and retrieve the best bid and ask prices.

<br>

- **`Trade`**: This is a data class that represents a trade that has been executed. It contains information such as:
  - `trade_id`: A unique identifier for the trade.
  - `order_id`: The identifier of the order that was matched.
  - `trader_id`: The identifier of the trader involved in the trade.
  - `price`: The price at which the trade was executed.
  - `quantity`: The amount of the asset that was traded.
  - `timestamp`: The time the trade occurred.

<br>

- **`MatchingEngine`**: This class is responsible for matching buy and sell orders.
  -  It takes an `OrderRequest` and tries to match it against existing orders in the `OrderBook`.
  -  If a match is found, it generates a `Trade` and updates the `OrderBook`.

### 🏃‍♀️ Running the Simulation
To see how these components work together, you can run the example simulation script:
```bash
python -m examples.simulation
```
This will simulate a series of order requests and print out the resulting trades and the final state of the order book.