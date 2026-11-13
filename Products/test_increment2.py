# =========================================================
# Increment 2 - Testing & Validation
# Prepared by Louis
# Purpose: Verify that the Order & Fulfilment Module
#          functions correctly.
# =========================================================

# Import standard Python libraries.
import json
import os
import time

# Import inventory function.
from inventory import load_products

# Import order management functions and status constants.
from order import (
    load_orders,
    list_orders,
    view_order_details,
    pack_order,
    update_order_status,
    STATUS_PACKED,
    STATUS_READY_FOR_DELIVERY,
    STATUS_OUT_FOR_DELIVERY,
    STATUS_DELIVERED,
    STATUS_CANCELLED
)

# Names of temporary files used for testing.
# This prevents changes to the actual products.json and orders.json.
TEST_PRODUCTS_FILE = "test_products.json"
TEST_FILE = "test_orders.json"

# ---------------------------------------------------------
# Create sample test data
# ---------------------------------------------------------

# Create a sample order dataset used by the test cases.
# The order starts in Pending status and is written to
# test_orders.json before the tests are executed.
sample_orders = [
    {
        "order_id": "O001",
        "customer_name": "Customer A",
        "delivery_address": "Test Address",
        "created_at": "2026-10-27T10:30:00",
        "status": "Pending",
        "items": [
            {
                "product_id": "P001",
                "product_name": "Notebook",
                "price": "25.00",
                "quantity": 2,
                "line_total": "50.00"
            }
        ],
        "total": "100.00",
        "delivery": None,
        "status_history": [
            {
                "status": "Pending",
                "at": "2026-10-27T10:30:00"
            }
        ]
    }
]

# Create matching products.
sample_products = [
    {
        "product_id": "P001",
        "product_name": "Notebook",
        "price": "25.00",
        "stock_quantity": 10
    }
]

# Create the initial test data files.
with open(TEST_FILE, "w", encoding="utf-8") as f:
    json.dump(sample_orders, f, indent=2)

with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
    json.dump(sample_products, f, indent=2)
    
# Store all test results for summary reporting.
results = []

# Save a test result and display it on screen.
def record(test_case, expected, actual, passed):
    status = "PASS" if passed else "FAIL"
    results.append(
        (
            test_case,
            expected,
            actual,
            status
        )
    )
    print("\n" + "-" * 60)
    print(f"Test Case      : {test_case}")
    print(f"Expected Result: {expected}")
    print(f"Actual Result  : {actual}")
    print(f"Result         : {status}")
print("=" * 60)
print("Increment 2 - Testing & Validation")
print("=" * 60)

# ---------------------------------------------------------
# Test 1 - List all orders
# ---------------------------------------------------------

try:
    # Retrieve all orders.
    orders = list_orders(
        path=TEST_FILE
    )

    # Verify the expected number of orders.
    passed = (
        len(orders) == 1
    )

    # Record PASS/FAIL result.
    record(
        "List all orders",
        "All orders returned successfully",
        f"{len(orders)} order(s) returned",
        passed
    )

# Catch any unexpected error.
except Exception as e:
    record(
        "List all orders",
        "All orders returned successfully",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 2 - View order details
# ---------------------------------------------------------

try:
    # View order details.
    order = view_order_details(
        "O001",
        path=TEST_FILE
    )

    # Check whether viewing was successful.
    passed = (
        order["order_id"] == "O001"
    )

    # Record PASS/FAIL result.
    record(
        "View order details",
        "Correct order information displayed",
        f"Order ID = {order['order_id']}",
        passed
    )

# Catch any unexpected error that occurs during this test.
# Store the error message in variable 'e'.
except Exception as e:

    # Record the error as the actual result.
    record(
        "View order details",
        "Correct order information displayed",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 3 - Mark order as packed
# ---------------------------------------------------------

try:
    # Mark order status as packed.
    order = update_order_status(
        "O001",
        STATUS_PACKED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record status result.
    record(
        "Mark order as packed",
        "Status changes to Packed",
        f"Status = {order['status']}",
        order["status"] == STATUS_PACKED
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Mark order as packed",
        "Status changes to Packed",
        str(e),      # Convert the error message to text.
        False        # Test failed.
    )

# ---------------------------------------------------------
# Test 4 - Update to Ready for Delivery
# ---------------------------------------------------------

try:
    # Update order status to Ready for Delivery.
    order = update_order_status(
        "O001",
        STATUS_READY_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record status result.
    record(
        "Update to Ready for Delivery",
        "Status changes successfully",
        f"Status = {order['status']}",
        order["status"] == STATUS_READY_FOR_DELIVERY
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Update to Ready for Delivery",
        "Status changes successfully",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 5 - Update to Out for Delivery
# ---------------------------------------------------------

try:
    # Update order status to Out for Delivery.
    order = update_order_status(
        "O001",
        STATUS_OUT_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record status result.
    record(
        "Update to Out for Delivery",
        "Status changes successfully",
        f"Status = {order['status']}",
        order["status"] == STATUS_OUT_FOR_DELIVERY
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Update to Out for Delivery",
        "Status changes successfully",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 6 - Update to Delivered
# ---------------------------------------------------------

try:
    # Update order status to Delivered.
    order = update_order_status(
        "O001",
        STATUS_DELIVERED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record status result.
    record(
        "Update to Delivered",
        "Status changes successfully",
        f"Status = {order['status']}",
        order["status"] == STATUS_DELIVERED
    )

# Catch an unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Update to Delivered",
        "Status changes successfully",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 7 - Cancel a Pending order
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
    
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)
               
    # Update order status to Cancelled.
    order = update_order_status(
        "O001",
        STATUS_CANCELLED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record status result.
    record(
        "Cancel a Pending order",
        "Status changes to Cancelled",
        f"Status = {order['status']}",
        order["status"] == STATUS_CANCELLED
    )

# Catch an unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Cancel a Pending order",
        "Status changes to Cancelled",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 8 - Cancel a Packed order
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
        
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)

    # Update order status to Packed.
    update_order_status(
        "O001",
        STATUS_PACKED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Update order status to Cancelled.
    update_order_status(
        "O001",
        STATUS_CANCELLED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record status result.
    record(
        "Cancel a Packed order",
        "Rejected",
        "Cancellation accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Cancel a Packed order",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 9 - Non-existing order
# ---------------------------------------------------------

try:
    # View a non-existing order.
    view_order_details(
        "O999",
        path=TEST_FILE,
    )

    # Record the status result.
    record(
        "Non-existing order",
        "Error displayed",
        "Order found",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Non-existing order",
        "Error displayed",
        "Order not found error raised",
        True
    )

# ---------------------------------------------------------
# Test 10 - Reopen program
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
        
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)

    # Update order status to Packed.
    update_order_status(
        "O001",
        STATUS_PACKED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Reload the order to verify that the updated status persists.
    reloaded_order = view_order_details(
        "O001",
        path=TEST_FILE
    )

    # Check whether the update was successful.
    passed = (
        reloaded_order["status"]
        == STATUS_PACKED
    )

    # Record PASS/FAIL result.    
    record(
        "Reopen program",
        "Status persists",
        f"Reloaded status = {reloaded_order['status']}",
        passed
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Reopen program",
        "Status persists",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 11 - Pending -> Ready for Delivery
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
        
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)
        
    # Update order status to Ready for Delivery.
    update_order_status(
        "O001",
        STATUS_READY_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record failure because the invalid transition was accepted.
    record(
        "Pending -> Ready for Delivery",
        "Rejected",
        "Transition accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Pending -> Ready for Delivery",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 12 - Pending -> Out for Delivery
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
        
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)
        
    # Update order status to Out for Delivery.
    update_order_status(
        "O001",
        STATUS_OUT_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record failure because the invalid transition was accepted.
    record(
        "Pending -> Out for Delivery",
        "Rejected",
        "Transition accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Pending -> Out for Delivery",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 13 - Pending -> Delivered
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
        
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)
        
    # Update order status to Delivered.
    update_order_status(
        "O001",
        STATUS_DELIVERED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record failure because the invalid transition was accepted.
    record(
        "Pending -> Delivered",
        "Rejected",
        "Transition accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Pending -> Delivered",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 14 - Packed -> Out for Delivery
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
        
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)

    # Update order status to Packed.
    update_order_status(
        "O001",
        STATUS_PACKED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Update order status to Out for Delivery.
    update_order_status(
        "O001",
        STATUS_OUT_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record failure because the invalid transition was accepted.
    record(
        "Packed -> Out for Delivery",
        "Rejected",
        "Transition accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Packed -> Out for Delivery",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 15 - Packed -> Delivered
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
        
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)
        
    # Update order status to Packed.
    update_order_status(
        "O001",
        STATUS_PACKED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Update order status to Delivered.
    update_order_status(
        "O001",
        STATUS_DELIVERED,
        path=TEST_FILE
    )

    # Record failure because the invalid transition was accepted.
    record(
        "Packed -> Delivered",
        "Rejected",
        "Transition accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Packed -> Delivered",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 16 - Ready for Delivery -> Delivered
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
        
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)
       
    # Update order status to Packed.
    update_order_status(
        "O001",
        STATUS_PACKED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Update order status to Ready for Delivery.
    update_order_status(
        "O001",
        STATUS_READY_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Update order status to Delivered.
    update_order_status(
        "O001",
        STATUS_DELIVERED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record failure because the invalid transition was accepted.
    record(
        "Ready for Delivery -> Delivered",
        "Rejected",
        "Transition accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Ready for Delivery -> Delivered",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 17 - Cancel a Ready for Delivery Order
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)

    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)
  
    # Update order status to Packed.
    update_order_status(
        "O001",
        STATUS_PACKED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Update order status to Ready for Delivery.
    update_order_status(
        "O001",
        STATUS_READY_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Update order status to Cancelled.
    update_order_status(
        "O001",
        STATUS_CANCELLED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record failure because the invalid transition was accepted.
    record(
        "Cancel a Ready for Delivery order",
        "Rejected",
        "Cancellation accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Cancel a Ready for Delivery order",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 18 - Cancel an Out for Delivery Order
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)

    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)
   
    # Update order status to Packed.
    update_order_status(
        "O001",
        STATUS_PACKED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Update order status to Ready for Delivery.
    update_order_status(
        "O001",
        STATUS_READY_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )
    
    # Update order status to Out for Delivery.
    update_order_status(
        "O001",
        STATUS_OUT_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )
    
    # Update order status to Cancelled.
    update_order_status(
        "O001",
        STATUS_CANCELLED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )
    
    # Record failure because the invalid transition was accepted.
    record(
        "Cancel an Out for Delivery order",
        "Rejected",
        "Cancellation accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Cancel an Out for Delivery order",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 19 - Cancel a Delivered Order
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)

    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)

    # Update order status to Packed.
    update_order_status(
        "O001",
        STATUS_PACKED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )
    
    # Update order status to Ready for Delivery.
    update_order_status(
        "O001",
        STATUS_READY_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )
    
    # Update order status to Out for Delivery.
    update_order_status(
        "O001",
        STATUS_OUT_FOR_DELIVERY,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )
    
    # Update order status to Delivered.
    update_order_status(
        "O001",
        STATUS_DELIVERED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )
    
    # Update order status to Cancelled.
    update_order_status(
        "O001",
        STATUS_CANCELLED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record failure because the invalid transition was accepted.
    record(
        "Cancel a Delivered order",
        "Rejected",
        "Cancellation accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Cancel a Delivered order",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 20 - Status History Update Verification
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)

    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)

    # Update order status to Packed.
    order = update_order_status(
        "O001",
        STATUS_PACKED,
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Retrieve the latest status recorded in the history.
    latest_status = (
        order["status_history"][-1]["status"]
    )

    # Count the number of status history entries.
    history_count = len(
        order["status_history"]
    )

    # Verify that the latest status is Packed and
    # a new status history entry was recorded.
    passed = (
        latest_status == STATUS_PACKED
        and history_count == 2
    )

    # Record PASS/FAIL result.
    record(
        "Status history update verification",
        "New status appended to status_history",
        (
            f"Latest status = {latest_status}, "
            f"Entries = {history_count}"
        ),
        passed
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Status history update verification",
        "New status appended to status_history",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 21 - Invalid Status Value
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
        
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)
        
    # Attempt to update the order using an invalid status value.
    update_order_status(
        "O001",
        "InvalidStatus",
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Record failure because the invalid transition was accepted.
    record(
        "Invalid status value",
        "Rejected",
        "Invalid status accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Invalid status value",
        "Rejected",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 22 - Empty Order File
# ---------------------------------------------------------

try:
    # Create an empty order file for boundary and equivalence partition testing.
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)

    # Load the orders.
    orders = load_orders(
        path=TEST_FILE
    )

    # Check whether the order quantity is zero.
    passed = (
        len(orders) == 0
    )

    # Record PASS/FAIL result.
    record(
        "Empty order file",
        "Zero orders loaded successfully",
        f"{len(orders)} orders loaded",
        passed
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Empty order file",
        "Zero orders loaded successfully",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 23 - Performance Test (100 Orders)
# ---------------------------------------------------------

try:
    # Create a test dataset containing 100 orders.
    performance_orders = []

    for i in range(1, 101):

        performance_orders.append(
            {
                "order_id": f"O{i:03}",
                "customer_name": f"Customer {i}",
                "delivery_address": "Test Address",
                "created_at": "2026-10-27T10:30:00",
                "status": "Pending",
                "items": [],
                "total": "100.00",
                "delivery": None,
                "status_history": [
                    {
                        "status": "Pending",
                        "at": "2026-10-27T10:30:00"
                    }
                ]
            }
        )

    # Write the 100-order dataset to the test file.
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(performance_orders, f, indent=2)
        
    # Measure order loading performance.
    start = time.time()
    orders = load_orders(path=TEST_FILE)
    end = time.time()
    duration = end - start

    # Record performance result.
    record(
        "Performance test (100 orders)",
        "100 orders loaded within 2 seconds",
        f"{len(orders)} orders loaded in {duration:.4f} seconds",
        len(orders) == 100 and duration < 2
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Performance test (100 orders)",
        "100 orders loaded within 2 seconds",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 24 - Pack order and deduct stock
# ---------------------------------------------------------

try:
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)

    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)

    # Pack the order to deduct inventory stock.
    pack_order(
        "O001",
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    # Reload the products file to check the remaining stock quantity.
    products = load_products(TEST_PRODUCTS_FILE)

    # Verify that the stock quantity was reduced from 10 to 8.
    passed = products[0]["stock_quantity"] == 8

    # Record PASS/FAIL result.
    record(
        "Pack order and deduct stock",
        "Stock quantity reduced from 10 to 8",
        f"Remaining quantity = {products[0]['stock_quantity']}",
        passed
    )

# Catch any unexpected error.
except Exception as e:
    record(
        "Pack order and deduct stock",
        "Stock quantity reduced from 10 to 8",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 25 - Pack order with insufficient stock
# ---------------------------------------------------------

try:
    # Temporarily set sample product stock to 1 (Order O001 requires 2).
    sample_products[0]["stock_quantity"] = 1
    
    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)

    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)

    try:
        # Attempt to pack the order when stock is insufficient.
        pack_order(
            "O001",
            path=TEST_FILE,
            products_path=TEST_PRODUCTS_FILE
        )
        passed = False
        actual = "No validation error raised"
        
    # Catch the expected validation error.
    except ValueError:
        passed = True
        actual = "Validation error raised"
    
    # Record PASS/FAIL result.
    record(
        "Pack order with insufficient stock",
        "Validation error raised",
        actual,
        passed
    )

# Catch any unexpected error.
except Exception as e:
    record(
        "Pack order with insufficient stock",
        "Validation error raised",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 26 - Pack same order twice
# ---------------------------------------------------------

try:
    # Reset sample product stock back to 10 so Test 26 can pack it successfully
    sample_products[0]["stock_quantity"] = 10

    # Reset the test data files back to their original state before each test.
    with open(TEST_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_products, f, indent=2)
        
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)
        
    # Pack the order for the first time successfully.
    pack_order(
        "O001",
        path=TEST_FILE,
        products_path=TEST_PRODUCTS_FILE
    )

    try:
        # Attempt to pack the same order a second time.
        pack_order(
            "O001",
            path=TEST_FILE,
            products_path=TEST_PRODUCTS_FILE
        )
        passed = False
        actual = "No validation error raised"
    # Catch the expected validation error.
    except ValueError:
        passed = True
        actual = "Validation error raised"

    # Record PASS/FAIL result.
    record(
        "Pack same order twice",
        "Validation error raised",
        actual,
        passed
    )

# Catch any unexpected error.
except Exception as e:
    record(
        "Pack same order twice",
        "Validation error raised",
        str(e),
        False
    )

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)

pass_count = 0
fail_count = 0

for item in results:

    test_case, expected, actual, status = item

    if status == "PASS":
        pass_count += 1
    else:
        fail_count += 1

    # Display the PASS/FAIL status for all test cases.
    print(
        f"{status:5} | {test_case}"
    )

# Calculate overall statistics.
total_tests = len(results)
pass_rate = (
    pass_count / total_tests * 100
)
print("\n" + "=" * 60)
print(
    f"Passed : {pass_count}/{total_tests}"
)
print(
    f"Failed : {fail_count}/{total_tests}"
)
print(
    f"Pass Rate: {pass_rate:.1f}%"
)
print("=" * 60)

# ---------------------------------------------------------
# Remove test file
# ---------------------------------------------------------

# Remove the temporary test files to ensure
# future test runs start with a clean environment.
if os.path.exists(TEST_PRODUCTS_FILE):
    os.remove(TEST_PRODUCTS_FILE)
    
if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)

print("\nTest files removed: test_products.json, test_orders.json")
