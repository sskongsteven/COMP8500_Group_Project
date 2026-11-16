import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

# File path for storing and loading order data records.
ORDERS_FILE = Path("orders.json")

# Define constant string values tracking delivery lifecycle stages.
STATUS_UNASSIGNED = "Unassigned"
STATUS_ASSIGNED = "Assigned"
STATUS_IN_TRANSIT = "In Transit"
STATUS_DELIVERED = "Delivered"

# Define constant string values representing available delivery methods.
DELIVERY_METHOD_COURIER = "Courier"
DELIVERY_METHOD_SELF_PICKUP = "Self Pickup"

# Dictionary mapping registered driver IDs to their respective driver names.
DRIVERS = {
    "D001": "Thomas",
    "D002": "David",
    "D003": "Peter"
}

# Load all customer orders from the JSON data file.
def load_orders(path=ORDERS_FILE):
    # Open and parse the orders JSON file.
    path = Path(path)
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} contains invalid JSON") from error

# Save the updated list of orders back to the JSON data file. 
def save_orders(orders, path=ORDERS_FILE):
    # Executes atomic serialized write-back to the local orders JSON file
    # using a temporary file to prevent file corruption.
    path = Path(path)
    temporary_path = None

    try:
        # Create a temporary file in the same directory
        with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                suffix=".tmp",
                delete=False,
        ) as file:
            temporary_path = Path(file.name)
            # Write orders data into the temporary file
            json.dump(orders, file, indent=2)
            file.flush()
            os.fsync(file.fileno())

        # Atomically replace the original file with the new temporary file
        os.replace(temporary_path, path)
    finally:
        # Ensure the temporary file is cleaned up if writing or replacing fails
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

# Locate a specific order record by its unique order ID.
def find_order(order_id, path=ORDERS_FILE):
    # Load the current orders list from storage.
    orders = load_orders(path)

    # Search through the list for a matching order ID.
    for order in orders:
        if order["order_id"] == order_id:
            return orders, order

    # Raise an error if no matching order ID exists.
    raise ValueError("Order not found.")

# Assign a delivery method and driver (if applicable) to a packed order.
def assign_delivery(order_id):
    # Retrieve the orders list and the target order record.
    orders, order = find_order(order_id)

    # Ensure only orders with a "Packed" status can be assigned.
    if order["status"] != "Packed":
        raise ValueError(
            "Only Packed orders can be assigned."
        )

    # Display the available delivery methods to the console.
    print("\nDelivery Methods")
    print("1. Courier")
    print("2. Self Pickup")

    # Read and verify the user's delivery method selection.
    method_choice = input(
        "Select delivery method: "
    ).strip()

    # Reference the delivery sub-dictionary for updates.
    delivery = order["delivery"]

    # Handle Courier delivery assignment and driver selection.
    if method_choice == "1":
        print("\nAvailable Drivers")

        # Iterate through the dictionary of registered drivers.
        for driver_id, name in DRIVERS.items():
            print(
                f"{driver_id} - {name}"
            )

        # Prompt staff to enter and format the target driver ID.
        driver_id = input(
            "\nDriver ID: "
        ).strip().upper()

        # Validate whether the entered driver ID exists.
        if driver_id not in DRIVERS:
            raise ValueError(
                "Invalid driver."
            )

        # Assign Courier as the chosen delivery method.
        delivery["delivery_method"] = (
            DELIVERY_METHOD_COURIER
        )

        # Record the assigned driver ID.
        delivery["driver_id"] = driver_id

        # Record the corresponding driver name.
        delivery["driver_name"] = (
            DRIVERS[driver_id]
        )

    # Handle Self Pickup assignment without a driver.
    elif method_choice == "2":
        delivery["delivery_method"] = (
            DELIVERY_METHOD_SELF_PICKUP
        )

        delivery["driver_id"] = None
        delivery["driver_name"] = None

    # Reject any input other than the available delivery method options.
    else:
        raise ValueError(
            "Invalid delivery method."
        )

    # Update the delivery status to Assigned.
    delivery["delivery_status"] = (
        STATUS_ASSIGNED
    )

    # Advance the overall order status to Ready for Delivery.
    new_status = "Ready for Delivery"
    order["status"] = new_status

    # Append a timestamped record to the order's status history trail.
    timestamp = datetime.now().isoformat()
    order["status_history"].append({"status": new_status, "at": timestamp})

    # Persist the updated orders database to disk.
    save_orders(orders)

    # Output a success confirmation message to the console.
    print(
        "\nDelivery assigned successfully."
    )

# Change the status of the assigned delivery to In Transit / Out for Delivery.
def start_delivery(order_id):
    orders, order = find_order(order_id)

    delivery = order["delivery"]

    if delivery["delivery_status"] != STATUS_ASSIGNED:
        raise ValueError(
            "Delivery must be Assigned."
        )

    delivery["delivery_status"] = (
        STATUS_IN_TRANSIT
    )

    new_status = "Out for Delivery"
    order["status"] = new_status

    timestamp = datetime.now().isoformat()
    order["status_history"].append({"status": new_status, "at": timestamp})

    save_orders(orders)

    print(
        "\nDelivery started successfully."
    )

# Mark an in-transit delivery as Delivered.
def complete_delivery(order_id):
    orders, order = find_order(order_id)

    delivery = order["delivery"]

    if delivery["delivery_status"] != STATUS_IN_TRANSIT:
        raise ValueError(
            "Delivery must be In Transit."
        )

    delivery["delivery_status"] = (
        STATUS_DELIVERED
    )

    new_status = "Delivered"
    order["status"] = new_status

    timestamp = datetime.now().isoformat()
    order["status_history"].append({"status": new_status, "at": timestamp})

    save_orders(orders)

    print(
        "\nDelivery completed successfully."
    )

# Display the delivery method, assigned driver, and delivery status of an order.
def view_delivery(order_id):
    _, order = find_order(order_id)

    delivery = order["delivery"]

    print("\nDelivery Information")
    print("--------------------")

    print(
        f"Method : "
        f"{delivery['delivery_method']}"
    )

    print(
        f"Driver ID : "
        f"{delivery['driver_id']}"
    )

    print(
        f"Driver Name : "
        f"{delivery['driver_name']}"
    )

    print(
        f"Status : "
        f"{delivery['delivery_status']}"
    )

# Display the current order status, delivery status, and full timestamped history.
def view_tracking(order_id):
    _, order = find_order(order_id)

    print("\nOrder Tracking")
    print("--------------------")

    print(
        f"Order ID : "
        f"{order['order_id']}"
    )

    print(
        f"Order Status : "
        f"{order['status']}"
    )

    print(
        f"Delivery Status : "
        f"{order['delivery']['delivery_status']}"
    )

    print("\nStatus History")

    for item in order["status_history"]:
        print(
            f"- {item['status']} "
            f"({item['at']})"
        )
