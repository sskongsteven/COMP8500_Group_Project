import json
from datetime import datetime

ORDERS_FILE = "orders.json"

# Strict Order Status Boundaries 
STATUS_PENDING = "Pending"
STATUS_PACKED = "Packed"
STATUS_READY_FOR_DELIVERY = "Ready for Delivery"
STATUS_OUT_FOR_DELIVERY = "Out for Delivery"
STATUS_DELIVERED = "Delivered"
STATUS_CANCELLED = "Cancelled"

def load_orders(path=ORDERS_FILE):
    """Reads and parses the text-based local orders.json file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_orders(orders, path=ORDERS_FILE):
    """Executes atomic serialized write-back to the local database file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=2)

def view_order_details(order_id, path=ORDERS_FILE):
    """
    Retrieves and displays a specific customer order record by its unique ID.
    """
    orders = load_orders(path)
    for order in orders:
        if order["order_id"] == order_id:
            return order
    raise ValueError(f"Order ID {order_id} was not found in the records.")

def update_order_status(order_id, new_status, path=ORDERS_FILE):
    """
    Every valid mutation automatically appends a timestamped log to status_history.
    """
    valid_statuses = [STATUS_PENDING, STATUS_PACKED, STATUS_READY_FOR_DELIVERY, STATUS_OUT_FOR_DELIVERY, STATUS_DELIVERED, STATUS_CANCELLED]
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status identifier token: {new_status}")

    orders = load_orders(path)
    for order in orders:
        if order["order_id"] == order_id:
            current_status = order["status"]
            
            # If target status matches current status, return without mutating logs
            if current_status == new_status:
                return order
                
            # Only a Pending order can become Packed.
            if new_status == STATUS_PACKED and current_status != STATUS_PENDING:
                raise ValueError(f"Rule Violation: Only Pending orders can transition to Packed. Current: {current_status}")
                
            # Only a Packed order can become Ready for Delivery.
            if new_status == STATUS_READY_FOR_DELIVERY and current_status != STATUS_PACKED:
                raise ValueError(f"Rule Violation: Only Packed orders can transition to Ready for Delivery. Current: {current_status}")
                
            # Only a Ready for Delivery order can become Out for Delivery.
            if new_status == STATUS_OUT_FOR_DELIVERY and current_status != STATUS_READY_FOR_DELIVERY:
                raise ValueError(f"Rule Violation: Only Ready for Delivery orders can transition to Out for Delivery. Current: {current_status}")
                
            # Only an Out for Delivery order can become Delivered.
            if new_status == STATUS_DELIVERED and current_status != STATUS_OUT_FOR_DELIVERY:
                raise ValueError(f"Rule Violation: Only Out for Delivery orders can transition to Delivered. Current: {current_status}")
                
            # A Pending order may be changed to Cancelled. Once Packed, it can no longer be Cancelled.
            if new_status == STATUS_CANCELLED:
                if current_status != STATUS_PENDING:
                    raise ValueError(f"Rule Violation: Orders can only be cancelled while Pending. Packing has already structuralized this order.")

            # Mutate state variables and record metadata
            order["status"] = new_status
            # Every status change must be recorded in status_history.
            timestamp = datetime.now().isoformat()
            order["status_history"].append({"status": new_status, "at": timestamp})
            
            save_orders(orders, path)
            return order
            
    raise ValueError(f"Order ID {order_id} was not found.")
