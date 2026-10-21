from decimal import Decimal, InvalidOperation
from storage import PRODUCTS_FILE, load_products, save_products


def valid_name(name):
    # Accept a non-empty product name.
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Product name cannot be empty")
    return name.strip()


def valid_price(price):
    # Return a non-negative price as a two-decimal-place string.
    try:
        # Convert in input to a decimal.
        amount = Decimal(str(price))
        if not amount.is_finite() or amount < 0:
            raise ValueError("Price must be zero or greater")
        if amount != amount.quantize(Decimal("0.01")):
            raise ValueError("Price cannot have more than two decimal places")
    except InvalidOperation as error:
        raise ValueError("Price must be a valid number") from error

    # A string avoids floating-point rounding in the JSON record.
    return f"{amount:.2f}"


def valid_stock(quantity):
    # Accept a non-negative whole number; reject booleans.
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Stock quantity must be a whole number")
    if quantity < 0:
        raise ValueError("Stock quantity cannot be negative")
    return quantity


def find_product(products, product_id):
    # Find a product in a loaded list.
    for product in products:
        if product["product_id"] == product_id:
            return product
    raise ValueError(f"Product {product_id} was not found")


def list_products(path=PRODUCTS_FILE):
    # Return all saved products.
    return load_products(path)


def add_product(name, price, starting_stock, path=PRODUCTS_FILE):
    # Validate and save a new product with an automatic ID.
    name = valid_name(name)
    price = valid_price(price)
    starting_stock = valid_stock(starting_stock)
    products = load_products(path)

    # This ID rule assumes products will not be permanently deleted.
    numbers = [
        int(product["product_id"][1:])
        for product in products
        if product["product_id"].startswith("P")
           and product["product_id"][1:].isdigit()
    ]
    product = {
        # Adjust the product ID into format, e.g. P009
        "product_id": f"P{max(numbers, default=0) + 1:03d}",
        "product_name": name,
        "price": price,
        "stock_quantity": starting_stock,
    }
    products.append(product)
    save_products(products, path)
    return product


def update_product(product_id, name=None, price=None, path=PRODUCTS_FILE):
    # Change a product's name, price, or both.
    if name is None and price is None:
        raise ValueError("Provide a name or price to update")

    new_name = valid_name(name) if name is not None else None
    new_price = valid_price(price) if price is not None else None
    products = load_products(path)
    product = find_product(products, product_id)

    if new_name is not None:
        product["product_name"] = new_name
    if new_price is not None:
        product["price"] = new_price

    save_products(products, path)
    return product


def change_stock(product_id, change, path=PRODUCTS_FILE):
    # Add stock with a positive number or remove it with a negative one.
    if isinstance(change, bool) or not isinstance(change, int) or change == 0:
        raise ValueError("Stock change must be a nonzero whole number")

    products = load_products(path)
    product = find_product(products, product_id)
    product["stock_quantity"] = valid_stock(
        product["stock_quantity"] + change
    )
    save_products(products, path)
    return product


def check_availability(product_id, quantity, path=PRODUCTS_FILE):
    # Return whether enough stock exists for a requested quantity.
    if valid_stock(quantity) == 0:
        raise ValueError("Requested quantity must be greater than zero")

    product = find_product(load_products(path), product_id)
    return product["stock_quantity"] >= quantity

