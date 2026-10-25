# COMP8500 Group Project — E-Shop Order Fulfillment and Delivery Management System

A console-based inventory and order fulfilment system for small e-shops, written in Python with
JSON file storage instead of a database server.

Course: COMP 8500SEF Software Engineering, HKMU · Group 65

## Scope

| Area | Status |
|---|---|
| Product and inventory management | In progress (Increment 1) |
| Customer ordering (sample order file) | Not started |
| Order fulfilment | Not started |
| Delivery management | Not started |
| Order tracking | Not started |

The project is built in three increments, and each one is reviewed before the next starts. So far the repository contains only the product and inventory part of Increment 1.

## Repository structure

    COMP8500_Group_Project/
    ├── README.md
    ├── .gitignore
    ├── Products/
    │   ├── storage.py          JSON read and write (atomic save)
    │   ├── inventory.py        Product and stock rules
    │   ├── inventory_menu.py   Console menu for inventory operations
    │   ├── products.json       Sample product data
    │   └── test.py             Seeds the sample products (see How to run)
    └── docs/
        └── 03-modules.md       Reference for every public function

## Requirements

- Python 3.12
- No third-party libraries; the standard library only

## How to run

The data file is opened by its relative path (products.json), so the program must be started
from the Products directory:

    cd Products
    python inventory_menu.py

At start-up the program tries to import inventory.py. If that import fails it prints a warning
and shows the menu in Mock Mode: the menu responds, but nothing is loaded or saved.

To populate the data file with the sample products, run:

    cd Products
    python test.py

The script adds the products listed in the file and prints the resulting inventory.

## Data file

Products/products.json holds a JSON list of product records:

    [
      {
        "product_id": "P001",
        "product_name": "Wireless Keyboard",
        "price": "120.00",
        "stock_quantity": 10
      }
    ]

| Field | Type | Rule |
|---|---|---|
| product_id | string | P followed by three digits; allocated as the highest existing number + 1 |
| product_name | string | Non-empty after trimming |
| price | string | Exactly two decimal places; stored as text to avoid floating-point rounding |
| stock_quantity | integer | Whole number, never negative |

## Documentation

| Document | Contents |
|---|---|
| docs/03-modules.md | Public function reference: inputs, outputs, raised errors and side effects |

## Open items

1. There is no main.py yet; inventory_menu.py is the only entry point.
2. Ordering, fulfilment, delivery and tracking will be added in later increments.
