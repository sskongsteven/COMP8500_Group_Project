import json
import os
import tempfile
from pathlib import Path

# Relative path to find the json file.
PRODUCTS_FILE = Path("products.json")


def load_products(path=PRODUCTS_FILE):
    # Return saved products, or an empty list on the first run.
    path = Path(path)
    if not path.exists():
        return []

    # Read and get the products from the json file.
    try:
        with path.open("r", encoding="utf-8") as file:
            products = json.load(file)
    except json.JSONDecodeError as error:
        # Do not treat a damaged file as an empty inventory.
        raise ValueError(f"{path} contains invalid JSON") from error

    # Check value in json file is a list or not.
    if not isinstance(products, list):
        raise ValueError(f"{path} must contain a list of products")
    return products


def save_products(products, path=PRODUCTS_FILE):
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
            # Write products data into temporary file
            json.dump(products, file, indent=2)
            file.flush()
            os.fsync(file.fileno())

        # Replacing the original file with the new temporary file.
        os.replace(temporary_path, path)
    finally:
        # Remove the temporary file if writing or replacing failed.
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

