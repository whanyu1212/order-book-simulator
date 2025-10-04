<!-- omit in toc -->
# Order Book Simulator
This repository contains proof-of-concept implementation of an Order Book Simulator in Python.

---

<!-- omit in toc -->
## Table of Content

- [Overview](#overview)
- [Getting Started](#getting-started)

### Overview
This project is a proof-of-concept implementation of an order book simulator, focusing on limit orders. It simulates the core functionalities of a financial market order book, including adding and canceling buy and sell limit orders.

### Getting Started
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