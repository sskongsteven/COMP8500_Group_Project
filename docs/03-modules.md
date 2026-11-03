# 4 Module reference

Every public function listed here exists in the repository at the time of writing.

## 4.1 storage.py

The module constant `PRODUCTS_FILE` points to `products.json` by a relative path, so the
program must be started from the `Products` directory.

### load_products(path=PRODUCTS_FILE) -> list

| Item | Detail |
|---|---|
| Input | path: the JSON file to read; defaults to `products.json` |
| Returns | The saved list of product records |
| Raises | `ValueError("<path> contains invalid JSON")` if the file does not parse; `ValueError("<path> must contain a list of products")` if the top level is not a list |
| Side effects | Reads `products.json` but does not modify it. A missing file returns an empty list instead of raising |

### save_products(products, path=PRODUCTS_FILE) -> None

| Item | Detail |
|---|---|
| Input | products: the list of records to save; path: the JSON file to write (defaults to `products.json`) |
| Returns | None — this function returns nothing |
| Raises | None — it does not validate its input |
| Side effects | Writes to a temporary file in the same directory, flushes it and syncs it to disk, then replaces `products.json` in a single step |

The save is deliberately not an in-place edit. If the program crashes while writing, the original
file is still intact and the temporary file is removed, so `products.json` can never be left half
written. Loading applies the opposite rule: a file that does not parse is reported as an error
rather than treated as an empty inventory, because an empty result would let the next save
overwrite the customer's data.

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
check availability and return to the main menu. Option 6 leaves the loop; because there is no
`main.py` yet, the program ends at that point.

Numeric fields are converted with `int()` before they reach the inventory functions, so text that is
not a number is reported with Python's own message (`invalid literal for int() with base 10: ...`)
rather than with a message from `valid_stock`.

## 4.4 main_menu.py

The module imports both menus at start-up: `inventory_menu` from Increment 1 and `order_menu` from
Increment 2. The delivery menu is a local placeholder until Increment 3.

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
| 3 | Delivery & Tracking Management | `display_delivery_menu()` (placeholder) |
| 0 | Exit | prints a closing message and leaves the loop |
| other | Invalid | prints "Invalid option. Please select a number from the menu." |

### display_delivery_menu() -> None

| Item | Detail |
|---|---|
| Input | None |
| Returns | None |
| Raises | Nothing |
| Side effects | Prints "Delivery & Tracking Module is under development." |

This function is temporary. It keeps the third menu option usable while the Delivery & Tracking
module is being built, and will be replaced by the real menu in Increment 3.

## 4.5 order.py

The module constant `ORDERS_FILE` points to `orders.json` by a relative path. Six status constants
define the only accepted status values: `STATUS_PENDING`, `STATUS_PACKED`,
`STATUS_READY_FOR_DELIVERY`, `STATUS_OUT_FOR_DELIVERY`, `STATUS_DELIVERED` and `STATUS_CANCELLED`.
Their values are the display strings used in the data file ("Pending", "Packed", "Ready for
Delivery", "Out for Delivery", "Delivered", "Cancelled").

### load_orders(path=ORDERS_FILE) -> list

| Item | Detail |
|---|---|
| Input | path: the JSON file to read; defaults to `orders.json` |
| Returns | The saved list of order records; an empty list when the file is missing |
| Raises | Nothing — a file that cannot be parsed is also returned as an empty list |
| Side effects | Reads `orders.json` but does not modify it |

### save_orders(orders, path=ORDERS_FILE) -> None

| Item | Detail |
|---|---|
| Input | orders: the list of order records to save; path: the JSON file to write |
| Returns | None |
| Raises | `OSError` or `TypeError` from the write, not wrapped |
| Side effects | Writes `orders.json` in place with `indent=2` |

### view_order_details(order_id, path=ORDERS_FILE) -> dict

| Item | Detail |
|---|---|
| Input | order_id: the identifier to look for, e.g. `O001` |
| Returns | The matching order record, including items, total and status_history |
| Raises | `ValueError("Order ID <id> was not found in the records.")` if no record has that identifier |
| Side effects | Reads `orders.json` but does not modify it |

### update_order_status(order_id, new_status, path=ORDERS_FILE) -> dict

| Item | Detail |
|---|---|
| Input | order_id; new_status: one of the six status constants |
| Returns | The updated order record. If the order already has that status, it is returned unchanged |
| Raises | `ValueError("Invalid status identifier token: <status>")` for a value outside the six; a `Rule Violation` error when the transition is not allowed from the current status; `ValueError("Order ID <id> was not found.")` for an unknown identifier |
| Side effects | Writes `orders.json` and appends `{"status": <new>, "at": <ISO timestamp>}` to status_history. Nothing is written when the request is rejected, or when the status is unchanged |

The five transition rules are enforced here rather than in the menu, so any future caller inherits
them. Requesting the current status is treated as a no-op and adds no history entry, which keeps
the history free of duplicate rows.

## 4.6 order_menu.py

At import time the module tries to import `order`. If that import fails it sets the internal
reference to `None`, prints a warning and continues in Mock Mode, where choices are echoed but no
order is read or written.

### display_order_menu() -> None

| Item | Detail |
|---|---|
| Input | None — the function reads the menu choice, the order ID and (for option 3) a status choice from the console |
| Returns | None — it returns when option 5 is chosen |
| Raises | Nothing itself. A `ValueError` from `order.py` is caught and printed with a prefix: `Query Denied`, `Transition Rejected`, `Update Aborted` or `Cancellation Refused` |
| Side effects | Prints the menu and results, and calls the order functions, which may write `orders.json` |

| Option | Action | Calls |
|---|---|---|
| 1 | View order details | `view_order_details(order_id)`; prints header, items, total and status history |
| 2 | Mark order as packed | `update_order_status(order_id, STATUS_PACKED)` |
| 3 | Update order status | asks for 1 Ready for Delivery, 2 Out for Delivery or 3 Delivered, then `update_order_status` |
| 4 | Cancel a pending order | `update_order_status(order_id, STATUS_CANCELLED)` |
| 5 | Return to the main menu | leaves the loop |

Packed and Cancelled have no entry of their own in option 3; they are reached through options 2
and 4, which keeps the two rule-bound transitions visible in the menu.
