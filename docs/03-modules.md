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
