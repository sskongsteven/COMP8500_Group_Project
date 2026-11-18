import json
import os
import tempfile
from pathlib import Path
from common import Order, Product

# Shared relative paths for the JSON data files.
PRODUCTS_FILE = Path("products.json")
ORDERS_FILE = Path("orders.json")


def _load_records(path, record_name):
    # Return saved records, or an empty list on the first run.
    path = Path(path)
    if not path.exists():
        return []

    # Read records from the JSON file.
    try:
        with path.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except json.JSONDecodeError as error:
        # Do not treat a damaged file as an empty dataset.
        raise ValueError(f"{path} contains invalid JSON") from error

    # Check value in json file is a list or not.
    if not isinstance(records, list):
        raise ValueError(f"{path} must contain a list of {record_name}")
    return records


def _save_records(records, path):
    # Write to a temporary file before replacing the saved file.
    path = Path(path)
    temporary_path = None

    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                suffix=".tmp",
                delete=False,
        ) as file:
            temporary_path = Path(file.name)
            # Write records into the temporary file.
            json.dump(records, file, indent=2)
            file.flush()
            os.fsync(file.fileno())

        # Replacing the original file with the new temporary file.
        os.replace(temporary_path, path)
    finally:
        # Remove the temporary file if writing or replacing failed.
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def load_products(path=PRODUCTS_FILE) -> list[Product]:
    return _load_records(path, "products")


def save_products(products: list[Product], path=PRODUCTS_FILE):
    _save_records(products, path)


def load_orders(path=ORDERS_FILE) -> list[Order]:
    return _load_records(path, "orders")


def save_orders(orders: list[Order], path=ORDERS_FILE):
    _save_records(orders, path)
