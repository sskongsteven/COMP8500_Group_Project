from datetime import datetime
from common import (
    Order, STATUS_PACKED, STATUS_READY_FOR_DELIVERY, STATUS_OUT_FOR_DELIVERY,
    STATUS_DELIVERED as ORDER_STATUS_DELIVERED,
    DELIVERY_STATUS_UNASSIGNED as STATUS_UNASSIGNED,
    DELIVERY_STATUS_ASSIGNED as STATUS_ASSIGNED,
    DELIVERY_STATUS_IN_TRANSIT as STATUS_IN_TRANSIT,
    DELIVERY_STATUS_DELIVERED as STATUS_DELIVERED,
    DELIVERY_METHOD_COURIER, DELIVERY_METHOD_SELF_PICKUP,
    new_delivery, new_status_history_entry,
)
from storage import ORDERS_FILE, load_orders, save_orders

# Dictionary mapping registered driver IDs to their respective driver names.
DRIVERS = {
    "D001": "Thomas",
    "D002": "David",
    "D003": "Peter"
}

# Locate a specific order record by its unique order ID.
def find_order(order_id, path=ORDERS_FILE) -> tuple[list[Order], Order]:
    # Load the current orders list from storage.
    orders = load_orders(path)

    # Search through the list for a matching order ID.
    for order in orders:
        if order["order_id"] == order_id:
            return orders, order

    # Raise an error if no matching order ID exists.
    raise ValueError("Order not found.")

# Assign a delivery method and driver (if applicable) to a packed order.
def assign_delivery(order_id, path=ORDERS_FILE):
    # Retrieve the orders list and the target order record.
    orders, order = find_order(order_id, path)

    # Ensure only orders with a "Packed" status can be assigned.
    if order["status"] != STATUS_PACKED:
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

    # Build a fresh delivery record; attach it only after inputs pass validation.
    delivery = new_delivery()

    # Handle Courier delivery assignment and driver selection.
    if method_choice == "1":
        print("\nAvailable Drivers")
        driver_list = list(DRIVERS.items())

        # Display a numbered list of registered drivers.
        for idx, (driver_id, name) in enumerate(driver_list, start=1):
            print(f"{idx}. {driver_id} - {name}")

        # Prompt staff to select a driver by number.
        driver_choice_str = input(
            "\nSelect driver: "
        ).strip()

        try:
            driver_choice = int(driver_choice_str)
        except ValueError:
            raise ValueError("Invalid driver.")

        if driver_choice < 1 or driver_choice > len(driver_list):
            raise ValueError("Invalid driver.")

        driver_id, driver_name = driver_list[driver_choice - 1]

        # Assign Courier as the chosen delivery method.
        delivery["delivery_method"] = (
            DELIVERY_METHOD_COURIER
        )

        # Record the assigned driver ID.
        delivery["driver_id"] = driver_id

        # Record the corresponding driver name.
        delivery["driver_name"] = driver_name

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

    order["delivery"] = delivery

    # Advance the overall order status to Ready for Delivery.
    new_status = STATUS_READY_FOR_DELIVERY
    order["status"] = new_status

    # Append a timestamped record to the order's status history trail.
    timestamp = datetime.now().isoformat()
    order["status_history"].append(new_status_history_entry(new_status, timestamp))

    # Persist the updated orders database to disk.
    save_orders(orders, path)

    # Output a success confirmation message to the console.
    print(
        "\nDelivery assigned successfully."
    )

# Change the status of the assigned delivery to In Transit / Out for Delivery.
def start_delivery(order_id, path=ORDERS_FILE):
    orders, order = find_order(order_id, path)

    delivery = order["delivery"]

    if delivery["delivery_status"] != STATUS_ASSIGNED:
        raise ValueError(
            "Delivery must be Assigned."
        )

    delivery["delivery_status"] = (
        STATUS_IN_TRANSIT
    )

    new_status = STATUS_OUT_FOR_DELIVERY
    order["status"] = new_status

    timestamp = datetime.now().isoformat()
    order["status_history"].append(new_status_history_entry(new_status, timestamp))

    save_orders(orders, path)

    print(
        "\nDelivery started successfully."
    )

# Mark an in-transit delivery as Delivered.
def complete_delivery(order_id, path=ORDERS_FILE):
    orders, order = find_order(order_id, path)

    delivery = order["delivery"]

    if delivery["delivery_status"] != STATUS_IN_TRANSIT:
        raise ValueError(
            "Delivery must be In Transit."
        )

    delivery["delivery_status"] = (
        STATUS_DELIVERED
    )

    new_status = ORDER_STATUS_DELIVERED
    order["status"] = new_status

    timestamp = datetime.now().isoformat()
    order["status_history"].append(new_status_history_entry(new_status, timestamp))

    save_orders(orders, path)

    print(
        "\nDelivery completed successfully."
    )

# Display the delivery method, assigned driver, and delivery status of an order.
def view_delivery(order_id, path=ORDERS_FILE):
    _, order = find_order(order_id, path)

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
def view_tracking(order_id, path=ORDERS_FILE):
    _, order = find_order(order_id, path)

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
