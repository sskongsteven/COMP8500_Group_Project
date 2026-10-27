# COMP8500SEF Group 65 Project — E-Shop Logistics Management System

A console-based inventory and order fulfilment system for small e-shops, written in Python with
JSON file storage instead of a database server.

Course: COMP 8500SEF Software Engineering, HKMU · Group 65

## Scope

| Area | Status |
|---|---|
| Product and inventory management | Completed (Increment 1) |
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
    │   ├── main_menu.py        Main entry point; routes to each module
    │   ├── test_increment1.py  Test script for Increment 1
    │   └── products.json       Sample product data
    └── docs/
        ├── 03-modules.md       Reference for every public function
        └── 04-increment-1.md   Workflow, test summary and limitations

## Requirements

- Python 3.12
- No third-party libraries; the standard library only

## How to run

The data file is opened by its relative path (products.json), so the program must be started from the Products directory:

    cd Products
    python main_menu.py

When the inventory area is opened, the program tries to import inventory.py. If that import fails it prints a warning and shows the menu in Mock Mode: the menu responds, but nothing is loaded or saved.

To run the Increment 1 tests:

    cd Products
    python test_increment1.py

The script runs twelve test cases against a temporary file, test_products.json, and prints a PASS or FAIL result for each, followed by a summary. The temporary file is deleted at the end, so the real products.json is never modified.

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
| docs/04-increment-1.md | Inventory workflow, test summary and limitations |

## Open items

1. main_menu.py is a preliminary version: options 2 (Order & Fulfilment) and 3 (Delivery & Tracking) are placeholders until Increment 2 and Increment 3 are built.
2. Ordering, fulfilment, delivery and tracking are not implemented yet.
