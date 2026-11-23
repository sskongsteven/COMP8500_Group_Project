# 4 Module reference

Every public function listed here exists in the repository at the time of writing.

## 4.1 storage.py

The module owns every read and write of the two JSON files.
`load_products` and `save_products` work on `products.json`; `load_orders` and `save_orders` work on `orders.json`. Both pairs go through the private helpers `_load_records` and `_save_records`, which hold the missing-file, invalid-JSON and list checks.

### load_products(path=PRODUCTS_FILE) -> list[Product]

| Item | Detail |
|---|---|
| Input | path: the JSON file to read; defaults to `products.json` |
| Returns | The list of product records; an empty list on the first run, when the file does not exist |
| Raises | `ValueError("<path> contains invalid JSON")` when the file cannot be parsed, and `ValueError("<path> must contain a list of products")` when the content is not a list |
| Side effects | Reads `products.json` but does not modify it |

### save_products(products, path=PRODUCTS_FILE) -> None

| Item | Detail |
|---|---|
| Input | products: the list of records to save; path: the JSON file to write |
| Returns | None |
| Raises | `OSError` from the write, not wrapped |
| Side effects | Writes a temporary file in the same directory, syncs it, then replaces the target file in one step |

### load_orders(path=ORDERS_FILE) -> list[Order]

| Item | Detail |
|---|---|
| Input | path: the JSON file to read; defaults to `orders.json` |
| Returns | The list of order records; an empty list when the file does not exist |
| Raises | `ValueError("<path> contains invalid JSON")` or `ValueError("<path> must contain a list of orders")` |
| Side effects | Reads `orders.json` but does not modify it |

### save_orders(orders, path=ORDERS_FILE) -> None

| Item | Detail |
|---|---|
| Input | orders: the list of records to save; path: the JSON file to write |
| Returns | None |
| Raises | `OSError` from the write, not wrapped |
| Side effects | Writes a temporary file in the same directory, syncs it, then replaces the target file in one step |

## 4.2 inventory.py

**Convention:** the `valid_*` and `find_*` helpers are pure — they check or look up and return a
value without touching the file. Only `add_product`, `update_product` and `change_stock` write to
`products.json`, and they do so through `save_products`.

### valid_name(name) -> str

| Item | Detail |
|---|---|
| Input | name: the product name entered by the user |
| Returns | The same name with leading and trailing spaces removed |
| Raises | `ValueError("Product name cannot be empty")` if the value is not a string, or is blank after trimming |
| Side effects | None |

### valid_price(price) -> str

| Item | Detail |
|---|---|
| Input | price: any value convertible to a decimal, typically the text the user typed (e.g. `12.50`) |
| Returns | The price as a string with exactly two decimal places, e.g. `"12.50"` |
| Raises | `ValueError("Price must be a valid number")` if it cannot be converted; `ValueError("Price must be zero or greater")` if it is negative or not finite; `ValueError("Price cannot have more than two decimal places")` if it carries fractions of a cent |
| Side effects | None |

The return value is a **string, not a float**, so that a price recorded as 120.00 is still exactly
120.00 when it is read back and summed across order lines. Binary floating point cannot represent
0.10 exactly, so storing prices as floats would allow rounding errors to accumulate.

### valid_stock(quantity) -> int

| Item | Detail |
|---|---|
| Input | quantity: a whole number entered by the user |
| Returns | The same quantity |
| Raises | `ValueError("Stock quantity must be a whole number")` if the value is a boolean or not an integer; `ValueError("Stock quantity cannot be negative")` if the value is negative |
| Side effects | None |

Booleans are rejected explicitly because in Python `True` is a subclass of `int`, so without that
check a boolean would be accepted as a stock quantity of 1.

### find_product(products, product_id) -> dict

| Item | Detail |
|---|---|
| Input | products: a list already loaded by the caller; product_id: the identifier to look for, e.g. `P001` |
| Returns | The matching product record |
| Raises | `ValueError("Product <id> was not found")` if no record has that identifier |
| Side effects | None — it searches the list it is given and does not read the file |

### list_products(path=PRODUCTS_FILE) -> list

| Item | Detail |
|---|---|
| Input | path: the JSON file to read; defaults to `products.json` |
| Returns | All saved product records; an empty list when the file does not exist yet |
| Raises | The errors raised by `load_products` (invalid JSON, or a top level that is not a list) |
| Side effects | Reads `products.json` but does not modify it |

This is a thin wrapper: it adds no filtering, sorting or validation of its own.

### add_product(name, price, starting_stock, path=PRODUCTS_FILE) -> dict

| Item | Detail |
|---|---|
| Input | name, price and starting_stock as entered by the user; path defaults to `products.json` |
| Returns | The new product record, including the identifier allocated to it |
| Raises | The validation errors from `valid_name`, `valid_price` and `valid_stock`; file errors from load and save |
| Side effects | Writes `products.json` with one record appended |

The identifier is `P` followed by three digits, allocated as the highest existing number plus one
(`P001`, `P002`, …). This rule assumes records are never permanently deleted; if deletion is added
later, deleting the highest-numbered product would allow its identifier to be reused.

### update_product(product_id, name=None, price=None, path=PRODUCTS_FILE) -> dict

| Item | Detail |
|---|---|
| Input | product_id; optionally a new name and/or a new price — at least one must be supplied |
| Returns | The updated product record |
| Raises | `ValueError("Provide a name or price to update")` if both are omitted; the validation errors from `valid_name` and `valid_price`; `ValueError("Product <id> was not found")` |
| Side effects | Writes `products.json`; nothing is written if validation fails |

Validation happens before the file is loaded, so an invalid update never reaches the save step.

### change_stock(product_id, change, path=PRODUCTS_FILE) -> dict

| Item | Detail |
|---|---|
| Input | product_id; change: a non-zero integer — positive adds stock, negative removes it |
| Returns | The updated product record |
| Raises | `ValueError("Stock change must be a nonzero whole number")` if change is zero, a bool, or not an integer; `ValueError("Stock quantity cannot be negative")` if the resulting quantity would fall below zero; `ValueError("Product <id> was not found")` |
| Side effects | Writes `products.json`; if the result would be negative, the error is raised before saving, so the file is unchanged |

Validation runs on the **resulting** quantity, not on the adjustment. That is what prevents stock
from going negative: removing 20 units from a stock of 5 fails as a negative quantity rather than
being accepted as a smaller number.

### check_availability(product_id, quantity, path=PRODUCTS_FILE) -> bool

| Item | Detail |
|---|---|
| Input | product_id; quantity: the number of units being requested — must be greater than zero |
| Returns | `True` when the recorded stock is at least the requested quantity, otherwise `False` |
| Raises | `ValueError("Requested quantity must be greater than zero")` when the requested quantity is zero; the validation errors from `valid_stock` for negative, non-integer or boolean values; `ValueError("Product <id> was not found")` |
| Side effects | Reads `products.json` but does not modify it |

## 4.3 inventory_menu.py

At import time the module tries to import `inventory`. If that import fails it sets the internal
reference to `None`, prints a warning and continues in Mock Mode: the menu still displays and echoes
each choice, but no data is read or written.

### display_inventory_menu() -> None

| Item | Detail |
|---|---|
| Input | None — the function reads the menu choice and the field values from the console |
| Returns | None — it returns when option 6 is chosen |
| Raises | Nothing itself. A `ValueError` from the inventory functions is caught and printed with a prefix (`Input Rejected`, `Update Aborted`, `Adjustment Refused`, `Query Denied`); option 1 catches any exception and prints a system error |
| Side effects | Reads console input, prints the menu and results, and calls the inventory functions, which may write `products.json` |

The menu offers six choices: view inventory, add product, update product information, change stock,
check availability and return to the main menu. Option 6 leaves the loop and returns to `main_menu.py`.

Numeric fields are converted with `int()` before they reach the inventory functions, so text that is
not a number is reported with Python's own message (`invalid literal for int() with base 10: ...`)
rather than with a message from `valid_stock`.

## 4.4 main_menu.py

The module imports three menus at start-up: `inventory_menu` from Increment 1, `order_menu` from
Increment 2 and `delivery_menu` from Increment 3.

### display_main_menu() -> None

| Item | Detail |
|---|---|
| Input | None — reads a single menu choice from the console |
| Returns | None — it returns when option 0 is chosen |
| Raises | Nothing itself; an unrecognised choice prints a message and the menu is shown again |
| Side effects | Prints the menu and opens the selected module menu, which may read or write the data files |

| Option | Action | Calls |
|---|---|---|
| 1 | Product & Inventory Management | `display_inventory_menu()` |
| 2 | Order & Fulfilment Management | `display_order_menu()` |
| 3 | Delivery & Tracking Management | `display_delivery_menu()` |
| 0 | Exit | prints a closing message and leaves the loop |
| other | Invalid | prints "Invalid option. Please select a number from the menu." |

## 4.5 order.py

The module holds the order rules. It reads and writes through `storage.py`, takes the status values
and the record types from `common.py`, and needs `inventory.py` to check stock. It owns two order
transitions only, Pending to Packed and Pending to Cancelled; the later states are applied by
`delivery.py`.

### list_orders(path=ORDERS_FILE) -> list[Order]

| Item | Detail |
|---|---|
| Input | path: the JSON file to read; defaults to `orders.json` |
| Returns | The full list of order records |
| Raises | Nothing of its own; `storage.py` raises on a damaged file |
| Side effects | Reads `orders.json` but does not modify it |

### view_order_details(order_id, path=ORDERS_FILE) -> Order

| Item | Detail |
|---|---|
| Input | order_id: the identifier to look for, e.g. `O001` |
| Returns | The matching order record, including items, total and status_history |
| Raises | `ValueError("Order ID <id> was not found in the records.")` |
| Side effects | Reads `orders.json` but does not modify it |

### pack_order(order_id, path=ORDERS_FILE, products_path=PRODUCTS_FILE) -> Order

| Item | Detail |
|---|---|
| Input | order_id; path: the order file; products_path: the product file to deduct from |
| Returns | The updated order record, now Packed |
| Raises | `ValueError`: "Order ID <id> was not found.", "Only Pending orders can be packed. Current: <status>", "Cannot pack an order with no items.", "Order item quantity must be greater than zero." or "Insufficient stock for <id>: required <n>, available <n>." |
| Side effects | Subtracts the quantities from the products, appends an entry to `status_history`, then writes `products.json` and `orders.json` |

### cancel_order(order_id, path=ORDERS_FILE) -> Order

| Item | Detail |
|---|---|
| Input | order_id; path: the order file |
| Returns | The updated order record, now Cancelled |
| Raises | `ValueError`: "Order ID <id> was not found." or "Only Pending orders can be cancelled." |
| Side effects | Appends an entry to `status_history`, writes `orders.json`, and does not touch stock |

## 4.6 order_menu.py

At import time the module tries to import `order`. If that import fails it sets the internal reference
to `None`, prints a warning and continues in Mock Mode, where choices are echoed but no order is read
or written.

### display_order_menu() -> None

| Item | Detail |
|---|---|
| Input | None — the function reads the menu choice and the order ID from the console |
| Returns | None — it returns when option 4 is chosen |
| Raises | Nothing itself. A `ValueError` from `order.py` is caught and printed with a prefix: `Query Denied`, `Transition Rejected` or `Cancellation Refused` |
| Side effects | Prints the menu and results, and calls the order functions, which may write `orders.json` and, when packing, `products.json` |

| Option | Action | Calls |
|---|---|---|
| 1 | View order details | `view_order_details(order_id)`; prints header, items, total and status history |
| 2 | Mark order as packed | `pack_order(order_id)`; checks stock, deducts it and saves both files |
| 3 | Cancel a pending order | `cancel_order(order_id)` |
| 4 | Return to the main menu | leaves the loop |
| other | Invalid | prints "Selection Rejected: Invalid command token. Please select an option bounded between 1 and 4." |

## 4.7 delivery.py

The module owns the delivery and tracking area. It reads and writes through `storage.py`, takes the
status values and the record types from `common.py`, and applies the three order states that follow
Packing. A delivery moves through `Unassigned`, `Assigned`, `In Transit` and `Delivered`.

### find_order(order_id, path=ORDERS_FILE) -> tuple

| Item | Detail |
|---|---|
| Input | order_id: the identifier to look for |
| Returns | A pair `(orders, order)`: the whole list and the matching record |
| Raises | `ValueError("Order not found.")` |
| Side effects | Reads `orders.json` but does not modify it |

### assign_delivery(order_id, path=ORDERS_FILE) -> None

| Item | Detail |
|---|---|
| Input | order_id; the delivery method is read from the console, and a driver ID when the method is Courier |
| Returns | None — it prints "Delivery assigned successfully." |
| Raises | `ValueError`: "Order not found.", "Only Packed orders can be assigned.", "Invalid delivery method." or "Invalid driver." |
| Side effects | Sets the method, the driver and `delivery_status = "Assigned"`, moves the order to "Ready for Delivery", appends to `status_history` and writes `orders.json` |

### start_delivery(order_id, path=ORDERS_FILE) -> None

| Item | Detail |
|---|---|
| Input | order_id |
| Returns | None — it prints "Delivery started successfully." |
| Raises | `ValueError`: "Order not found." or "Delivery must be Assigned." |
| Side effects | Sets `delivery_status = "In Transit"` and the order to "Out for Delivery", appends to `status_history` and writes `orders.json` |

### complete_delivery(order_id, path=ORDERS_FILE) -> None

| Item | Detail |
|---|---|
| Input | order_id |
| Returns | None — it prints "Delivery completed successfully." |
| Raises | `ValueError`: "Order not found." or "Delivery must be In Transit." |
| Side effects | Sets `delivery_status = "Delivered"` and the order to "Delivered", appends to `status_history` and writes `orders.json` |

### view_delivery(order_id, path=ORDERS_FILE) -> None

| Item | Detail |
|---|---|
| Input | order_id |
| Returns | None — it prints the method, the driver ID, the driver name and the delivery status |
| Raises | `ValueError("Order not found.")` |
| Side effects | Reads `orders.json` but does not modify it |

### view_tracking(order_id, path=ORDERS_FILE) -> None

| Item | Detail |
|---|---|
| Input | order_id |
| Returns | None — it prints the order ID, the order status, the delivery status and every entry in `status_history` |
| Raises | `ValueError("Order not found.")` |
| Side effects | Reads `orders.json` but does not modify it |

## 4.8 delivery_menu.py

### display_delivery_menu() -> None

| Item | Detail |
|---|---|
| Input | None — it reads the menu choice, the order selection and, for option 2, the delivery method and driver from the console |
| Returns | None — it returns when option 6 is chosen |
| Raises | Nothing itself. A `ValueError` from `delivery.py` is caught and printed with a prefix: `Assignment Rejected`, `Transition Rejected`, `Completion Rejected` or `Query Denied` |
| Side effects | Prints the menu and the results, and calls the delivery functions, which may write `orders.json` |

| Option | Action | Calls |
|---|---|---|
| 1 | View Delivery Details | `view_delivery(order_id)`; prints method, driver and delivery status |
| 2 | Assign Delivery | `assign_delivery(order_id)`; asks for the method, then the driver for Courier |
| 3 | Start Delivery | `start_delivery(order_id)` |
| 4 | Complete Delivery | `complete_delivery(order_id)` |
| 5 | View Order Tracking | `view_tracking(order_id)`; prints the whole status history |
| 6 | Return to Main Menu | leaves the loop |
| other | Invalid | prints "Selection Rejected: Invalid command token. Please select an option bounded between 1 and 6." |

## 4.9 common.py

The module holds the values and record types that the other modules share, so a status string or a
field name is written once. It also provides three factory functions, which return a fresh dictionary
each time rather than a shared template.

| Name | Value |
|---|---|
| `STATUS_PENDING` … `STATUS_CANCELLED` | The six order statuses: Pending, Packed, Ready for Delivery, Out for Delivery, Delivered, Cancelled |
| `ORDER_STATUSES` | A tuple of the six order statuses |
| `DELIVERY_STATUS_UNASSIGNED` … `DELIVERY_STATUS_DELIVERED` | The four delivery statuses; `DELIVERY_STATUS_DELIVERED` is the same string as `STATUS_DELIVERED` |
| `DELIVERY_STATUSES` | A tuple of the four delivery statuses |
| `DELIVERY_METHOD_COURIER`, `DELIVERY_METHOD_SELF_PICKUP` | "Courier" and "Self Pickup" |

The module also declares the record shapes with `TypedDict`: `Product`, `OrderLine`, `Delivery`,
`StatusHistoryEntry` and `Order`. A `TypedDict` documents the fields for the reader and the type
checker; it performs no runtime validation, so the rules stay in `inventory.py`, `order.py` and
`delivery.py`.

### new_product(product_id, product_name, price, stock_quantity) -> Product

| Item | Detail |
|---|---|
| Input | The four field values of a product record |
| Returns | A new `Product` dictionary |
| Raises | Nothing |
| Side effects | None — it only builds a dictionary |

### new_delivery() -> Delivery

| Item | Detail |
|---|---|
| Input | None |
| Returns | A new `Delivery` dictionary with method Courier, no driver and status Unassigned |
| Raises | Nothing |
| Side effects | None — a fresh dictionary is returned for each call, so two orders never share one |

### new_status_history_entry(status, timestamp) -> StatusHistoryEntry

| Item | Detail |
|---|---|
| Input | status: the new status; timestamp: an ISO date and time string |
| Returns | A new `StatusHistoryEntry` dictionary |
| Raises | Nothing |
| Side effects | None — it only builds a dictionary |

## 4.10 web_app.py

The module serves a browser interface over the same `inventory.py`, `order.py` and `delivery.py`, so
the console menus and the page change the same two data files. It starts an HTTP server on
`127.0.0.1:8000`, serves one page, and answers two JSON routes: `GET /` returns the page, `GET
/api/state` returns the current data for it, and `POST /` applies the change the page asks for.

### capture_initial_snapshot() -> None

| Item | Detail |
|---|---|
| Input | None |
| Returns | None |
| Raises | Nothing |
| Side effects | Reads both data files once and keeps a copy in memory, so the page can restore the starting data |

### build_state_payload() -> dict

| Item | Detail |
|---|---|
| Input | None |
| Returns | A dictionary holding the products, the orders and the delivery state, ready to be sent as JSON |
| Raises | Nothing of its own; a damaged data file raises from `storage.py` |
| Side effects | Reads both data files but does not modify them |

### assign_delivery_non_interactive(order_id, ...) -> None

| Item | Detail |
|---|---|
| Input | order_id and the chosen method and driver, taken from the page instead of the console |
| Returns | None |
| Raises | The same `ValueError` messages as `delivery.assign_delivery` |
| Side effects | Applies the same change as the console menu: `orders.json` is written |

### run_server(host="127.0.0.1", port=8000, open_browser=True) -> None

| Item | Detail |
|---|---|
| Input | host and port to listen on; open_browser: whether to open the page automatically |
| Returns | None — it runs until the process is stopped |
| Raises | `OSError` when the port is already in use |
| Side effects | Starts the HTTP server, serves the page and the JSON routes, and writes the data files when a change is applied |
