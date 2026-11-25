# COMP 8500SEF Group 65 Project — E-Shop Logistics Management System

A console-based inventory, order fulfilment, delivery and order tracking system for small e-shops, written in Python with JSON file storage instead of a database server.

Course: COMP 8500SEF Software Engineering, HKMU · Group 65

## Scope

| Area |
|---|
| Product and inventory management (Increment 1) |
| Customer ordering (sample order file) (Increment 2) |
| Order fulfilment (Increment 2) |
| Delivery management (Increment 3) |
| Order tracking (Increment 3) |
| Web interface (browser version of the same modules) |

The project is built in three increments, and each one is reviewed before the next starts. All three
are delivered: product and inventory management, order fulfilment, and delivery and tracking. The
repository also contains a browser interface that reuses the same modules, and unit tests for each
menu and increment.

## Repository structure

    COMP8500_Group_Project/
    ├── README.md
    ├── .gitignore
    ├── Products/
    │   ├── common.py             Shared status values and record types
    │   ├── storage.py            JSON read and write (atomic save)
    │   ├── inventory.py          Product and stock rules
    │   ├── inventory_menu.py     Console menu for inventory operations
    │   ├── order.py              Order records, packing and cancellation
    │   ├── order_menu.py         Console menu for order operations
    │   ├── delivery.py           Delivery assignment and tracking rules
    │   ├── delivery_menu.py      Console menu for delivery operations
    │   ├── main_menu.py          Main entry point; routes to each module
    │   ├── web_app.py            Browser interface over the same modules
    │   ├── products.json         Sample product data
    │   ├── orders.json           Sample order data
    │   ├── test_increment1.py    Unit tests for increment 1
    │   ├── test_increment2.py    Unit tests for increment 2
    │   ├── test_increment3.py    Unit tests for increment 3
    │   ├── test_inventory_menu.py  Unit tests for the inventory menu
    │   ├── test_order_menu.py      Unit tests for the order menu
    │   ├── test_delivery_menu.py   Unit tests for the delivery menu
    │   └── test_main_menu.py       Unit tests for the main menu
    └── docs/
        ├── 03-modules.md         Reference for every public function
        ├── 04-increment-1.md     Inventory workflow, test summary and limitations
        ├── 05-increment-2.md     Order workflow, test summary and limitations
        └── 06-increment-3.md     Delivery workflow, test summary and limitations

## Requirements

- Python 3.12
- No third-party libraries; the standard library only

## How to run

The data files are opened by their relative paths (products.json and orders.json), so the program must be started from the Products directory:

    cd Products
    python main_menu.py

All three areas are implemented. Product and Inventory Management covers viewing, adding products,updating details and changing stock. Order and Fulfilment Management offers view, pack, cancel and return; packing deducts the stock and writes both files. Delivery and Tracking Management offers view, assign, start, complete and tracking, and each delivery step moves the order on as well.

At start-up the program imports inventory.py through inventory_menu.py. If that import fails, a warning is printed and the inventory menu runs in Mock Mode: the menu responds, but nothing is loaded or saved.

To run the tests:

    cd Products
    python -m unittest test_increment1 test_increment2 test_increment3
    python -m unittest test_inventory_menu test_order_menu test_delivery_menu test_main_menu

The suites use the `unittest` framework. They run against temporary data files that they create and delete, so the real `products.json` and `orders.json` are never modified.

## Data files

Products/products.json holds a JSON list of product records:

    [
      {
        "product_id": "P001",
        "product_name": "Notebook",
        "price": "25.00",
        "stock_quantity": 11
      }
    ]

| Field | Type | Rule |
|---|---|---|
| product_id | string | P followed by three digits; allocated as the highest existing number + 1 |
| product_name | string | Non-empty after trimming |
| price | string | Exactly two decimal places; stored as text to avoid floating-point rounding |
| stock_quantity | integer | Whole number, never negative |

Products/orders.json holds a JSON list of order records:

    [
      {
        "order_id": "O001",
        "customer_name": "Sample Customer A",
        "delivery_address": "Sample address, Central, Hong Kong",
        "created_at": "2026-10-27T10:30:00",
        "status": "Pending",
        "items": [
          {
            "product_id": "P001",
            "product_name": "Notebook",
            "price": "25.00",
            "quantity": 2,
            "line_total": "50.00"
          },
          {
            "product_id": "P002",
            "product_name": "Ballpoint Pen",
            "price": "6.00",
            "quantity": 3,
            "line_total": "18.00"
          }
        ],
        "total": "68.00",
        "delivery": {
          "delivery_method": "Courier",
          "driver_id": null,
          "driver_name": null,
          "delivery_status": "Unassigned"
        },
        "status_history": [
          { "status": "Pending", "at": "2026-10-27T10:30:00" }
        ]
      }
    ]

| Field | Type | Rule |
|---|---|---|
| order_id | string | Generated by the program; never reused |
| customer_name | string | Any string |
| delivery_address | string | Any string |
| created_at | string | Date and time the order was created |
| status | string | Pending, Packed, Ready for Delivery, Out for Delivery, Delivered or Cancelled |
| items | list | Each item has product_id, product_name, price, quantity and line_total |
| total | string | Total price, two decimal places; equal to the sum of the line totals |
| delivery | object or null | Set when a delivery is assigned: delivery_method, driver_id, driver_name and delivery_status. Null only if no delivery has been assigned yet |
| status_history | list | One entry per status change, each with status and the time it happened |

Status transitions follow a fixed order: Pending to Packed to Ready for Delivery to Out for Delivery to Delivered. A Pending order may also be cancelled; once an order is Packed it can no longer be cancelled. Every change is appended to status_history. Packing an order deducts its items from stock; if stock is insufficient, the order stays Pending.

Orders are not created inside the application in this release; the menus work from the sample order file. Manual order entry is not implemented yet.

## Documentation

| Document | Contents |
|---|---|
| docs/03-modules.md | Public function reference: inputs, outputs, raised errors and side effects |
| docs/04-increment-1.md | Inventory workflow, test summary and limitations |
| docs/05-increment-2.md | Order workflow, test summary and limitations |
| docs/06-increment-3.md | Delivery workflow, test summary and limitations |

## Open items

1. Delivery management and order tracking are implemented; delivery assignment cannot be changed once made, and the driver list is fixed in the code.
2. Manual order entry is not implemented; the order menus work from the sample order file.
