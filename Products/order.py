from datetime import datetime
from common import (
    Order, STATUS_PENDING, STATUS_PACKED, STATUS_CANCELLED,
    new_status_history_entry,
)
from inventory import find_product, valid_stock
from storage import (
    PRODUCTS_FILE, ORDERS_FILE, load_products, save_products,
    load_orders, save_orders,
)

# load_orders/save_orders are imported here for existing callers; storage owns them.

def list_orders(path=ORDERS_FILE) -> list[Order]:
    """
    FUNCTION: Returns the full list of saved orders.
    """
    return load_orders(path)

def view_order_details(order_id, path=ORDERS_FILE) -> Order:
    """
    Retrieves and displays a specific customer order record by its unique ID.
    """
    orders = load_orders(path)
    for order in orders:
        if order["order_id"] == order_id:
            return order
    raise ValueError(f"Order ID {order_id} was not found in the records.")

def pack_order(order_id, path=ORDERS_FILE, products_path=PRODUCTS_FILE) -> Order:
    """Check every item, then deduct stock once and mark a Pending order Packed."""
    orders = load_orders(path)
    order = next((record for record in orders if record["order_id"] == order_id), None)
    if order is None:
        raise ValueError(f"Order ID {order_id} was not found.")
    if order["status"] != STATUS_PENDING:
        raise ValueError(f"Only Pending orders can be packed. Current: {order['status']}")
    if not order["items"]:
        raise ValueError("Cannot pack an order with no items.")

    # Combine repeated product lines so their total cannot exceed available stock.
    required = {}
    for item in order["items"]:
        quantity = valid_stock(item["quantity"])
        if quantity == 0:
            raise ValueError("Order item quantity must be greater than zero.")
        product_id = item["product_id"]
        required[product_id] = required.get(product_id, 0) + quantity

    products = load_products(products_path)
    deductions = []
    for product_id, quantity in required.items():
        product = find_product(products, product_id)
        available = valid_stock(product["stock_quantity"])
        if available < quantity:
            raise ValueError(
                f"Insufficient stock for {product_id}: required {quantity}, available {available}."
            )
        deductions.append((product, quantity))

    # All checks passed. No file is changed when an item fails validation.
    for product, quantity in deductions:
        product["stock_quantity"] -= quantity
    order["status"] = STATUS_PACKED
    order["status_history"].append(
        new_status_history_entry(STATUS_PACKED, datetime.now().isoformat())
    )
    save_products(products, products_path)
    save_orders(orders, path)
    return order

def cancel_order(order_id, path=ORDERS_FILE) -> Order:
    """Cancel a Pending order without changing product stock."""
    orders = load_orders(path)
    for order in orders:
        if order["order_id"] == order_id:
            if order["status"] != STATUS_PENDING:
                raise ValueError("Only Pending orders can be cancelled.")
            order["status"] = STATUS_CANCELLED
            order["status_history"].append(
                new_status_history_entry(STATUS_CANCELLED, datetime.now().isoformat())
            )
            save_orders(orders, path)
            return order
    raise ValueError(f"Order ID {order_id} was not found.")
