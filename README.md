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
- [💡 Motivation and Improvements Over Classroom Approach](#-motivation-and-improvements-over-classroom-approach)
- [⚠️ Known Limitations](#️-known-limitations)

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
  - `TradeHistoryTracker`: Tracks and analyzes trade history.

- **`database`**: This module handles all database interactions. It includes:
  - `models`: Defines the database schema for orders, trades, and trader accounts.
  - `session`: Manages database sessions and connections.

- **`main`**: This is the entry point of the application. It initializes the FastAPI app and includes the API router.

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

> **Note:** The legacy script does not `await` the `ConnectionManager`, but the simulation can still run.

---

### 💡 Motivation and Improvements Over Classroom Approach

This project attempts to address several limitations observed in classroom order book simulations:

**Identified Pain Points:**
- **Lack of Runtime Validation**: The Google Form-based order submission system lacks runtime error handling, allowing students to submit invalid values (e.g., string inputs for numerical fields such as `Price`).
- **Missing Edge Case Handling**: The original sample code does not implement safeguards to prevent self-trading or handle crossed book scenarios, which are critical considerations in real-world order matching systems.
- **Post-Processing vs. Real-Time Execution**: The original approach processes a flat file of collected orders after all submissions are complete, rather than handling orders as they stream in. This differs significantly from actual trading systems that process orders immediately upon arrival.

**Implemented Solutions:**
- **Robust Data Validation**: Leveraged Pydantic models for comprehensive runtime validation, ensuring type safety and data integrity. All order requests are validated at the API level before processing. Key design decisions include:
  - **UUID for Trader Identification**: Instead of using raw group numbers or sequential IDs, UUIDs are employed to uniquely identify traders. This approach enhances privacy by preventing inference of trader count or registration order, while also ensuring global uniqueness across distributed systems.
  - **Unix Timestamps**: Timestamps are stored as Unix epoch floats rather than datetime objects for improved serialization efficiency, simplified cross-timezone handling, and seamless JSON compatibility in API responses.
  - **Mandatory Trader Registration**: Traders must register before submitting orders, mimicking real-world exchange requirements. This enables proper account management, balance tracking, trade attribution, and provides a foundation for implementing credit checks, position limits, and risk management controls that are essential in actual trading systems.
  - **Order Priority Framework**: Included a `Priority` field (HIGH, MEDIUM, LOW) in the order schema, though it is currently not used in the matching logic. This field is primarily a structural placeholder for extensibility. While most real-world exchanges follow strict price-time priority for fairness and regulatory compliance, some systems do implement prioritization for certain order types (e.g., market orders over limit orders, or cancel requests during high-volume periods). This level of complexity is beyond the scope of the current implementation.
- **Edge Case Management**: Implemented self-trading prevention logic and crossed book detection with real-time alerts through the `MetricsCalculator` class, mirroring production trading system safeguards.
- **(Close to)Real-Time Order Processing with WebSocket Support**: Built a FastAPI-based web server that processes orders immediately upon arrival, simulating the continuous operation of actual trading platforms. Orders are matched and executed in real-time rather than batch-processed from flat files. The current WebSocket implementation broadcasts all trades to all connected clients; a production system would require targeted messaging to send trader-specific events (order confirmations, fills, cancellations) only to the relevant participants for improved efficiency and privacy.
- **Production-Inspired Architecture**: Designed with separation of concerns and modular components including order matching, account management, database persistence, and real-time trade broadcasting. While not fully production-ready (would require API deployment to public endpoints, managed database services, enhanced WebSocket infrastructure, and a dedicated frontend UI), this implementation demonstrates industry-standard design patterns and best practices.

---

### ⚠️ Known Limitations

While this simulator addresses some pain points from traditional classroom approaches, it remains a proof-of-concept with several limitations:

**Technical Limitations:**
- **Local Deployment Only**: The API runs locally and is not deployed to a public endpoint, limiting accessibility for distributed teams or remote collaboration.
- **SQLite Database**: Uses SQLite for simplicity, which is not suitable for production workloads. A production system would require managed database services (PostgreSQL, MySQL, or specialized time-series databases) with proper replication, backup, and high-availability configurations.
- **Basic WebSocket Implementation**: Currently broadcasts all trades to all connected clients rather than implementing targeted, trader-specific messaging channels. Lacks authentication, session management, and reconnection handling.
- **No Frontend UI**: Interaction is limited to API endpoints and command-line scripts. A production system would benefit from a dedicated web interface for order submission, market visualization, and portfolio management.
- **Single-Threaded Processing**: The current implementation processes orders sequentially. High-frequency trading systems require concurrent processing, message queues, and sophisticated load balancing.

**Feature Limitations:**
- **Limit Orders Only**: Does not support other order types such as market orders, stop-loss orders, iceberg orders, or fill-or-kill orders commonly found in real exchanges.
- **No Order Cancellation/Modification**: While the architecture supports it, explicit endpoints for order cancellation or modification are not fully implemented.
- **Simplified Fee Structure**: Does not implement maker/taker fees, tiered fee schedules, or rebate programs typical of modern exchanges.
- **Basic Risk Management**: Lacks sophisticated risk controls such as circuit breakers, position limits per trader, maximum order size validation, or margin requirements.
- **No Market Data Feeds**: Does not provide historical tick data, OHLC (Open-High-Low-Close) aggregations, or market depth snapshots that traders rely on for analysis.
- **Unused Priority Field**: The `Priority` field exists in the schema but is not utilized in matching logic, as discussed above.

**Scalability and Performance:**
- **No Load Testing**: The system has not been stress-tested under high-volume conditions or with thousands of concurrent orders.
- **Lack of Monitoring**: Does not include observability tools, metrics dashboards, or alerting systems that would be essential for operating a production service.
- **No Disaster Recovery**: Lacks backup strategies, failover mechanisms, or disaster recovery procedures.

These limitations represent opportunities for future enhancement and learning, making this project an educational foundation rather than a production-ready trading platform.