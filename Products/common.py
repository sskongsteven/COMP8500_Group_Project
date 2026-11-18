"""Shared record definitions and status values for all three increments.

TypedDict describes ordinary JSON-compatible dictionaries; it does not perform
runtime validation. Business rules remain in inventory.py, order.py and delivery.py.
"""
from typing import TypedDict


# Order status values.
STATUS_PENDING = "Pending"
STATUS_PACKED = "Packed"
STATUS_READY_FOR_DELIVERY = "Ready for Delivery"
STATUS_OUT_FOR_DELIVERY = "Out for Delivery"
STATUS_DELIVERED = "Delivered"
STATUS_CANCELLED = "Cancelled"
ORDER_STATUSES = (
    STATUS_PENDING, STATUS_PACKED, STATUS_READY_FOR_DELIVERY,
    STATUS_OUT_FOR_DELIVERY, STATUS_DELIVERED, STATUS_CANCELLED,
)

# Delivery status values are separate from overall order statuses.
DELIVERY_STATUS_UNASSIGNED = "Unassigned"
DELIVERY_STATUS_ASSIGNED = "Assigned"
DELIVERY_STATUS_IN_TRANSIT = "In Transit"
DELIVERY_STATUS_DELIVERED = STATUS_DELIVERED
DELIVERY_STATUSES = (
    DELIVERY_STATUS_UNASSIGNED, DELIVERY_STATUS_ASSIGNED,
    DELIVERY_STATUS_IN_TRANSIT, DELIVERY_STATUS_DELIVERED,
)
DELIVERY_METHOD_COURIER = "Courier"
DELIVERY_METHOD_SELF_PICKUP = "Self Pickup"


class Product(TypedDict):
    product_id: str
    product_name: str
    price: str
    stock_quantity: int


class OrderLine(TypedDict):
    product_id: str
    product_name: str
    price: str
    quantity: int
    line_total: str


class Delivery(TypedDict):
    delivery_method: str
    driver_id: str | None
    driver_name: str | None
    delivery_status: str


class StatusHistoryEntry(TypedDict):
    status: str
    at: str


class Order(TypedDict):
    order_id: str
    customer_name: str
    delivery_address: str
    created_at: str
    status: str
    items: list[OrderLine]
    total: str
    delivery: Delivery
    status_history: list[StatusHistoryEntry]


def new_product(product_id, product_name, price, stock_quantity) -> Product:
    return Product(product_id=product_id, product_name=product_name,
                   price=price, stock_quantity=stock_quantity)


def new_delivery() -> Delivery:
    # Return a fresh dictionary for each order, rather than a shared template.
    return Delivery(delivery_method=DELIVERY_METHOD_COURIER, driver_id=None,
                    driver_name=None, delivery_status=DELIVERY_STATUS_UNASSIGNED)


def new_status_history_entry(status, timestamp) -> StatusHistoryEntry:
    return StatusHistoryEntry(status=status, at=timestamp)
