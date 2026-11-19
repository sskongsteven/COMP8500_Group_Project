# =========================================================
# Increment 3 - Testing & Validation
# Author: CHEN ZHI YANG
# Target: Verify the Delivery & Tracking Module
#          functions correctly based on the Testing Plan.
# =========================================================

import io
import json
import os
import time
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import delivery
import storage

# Temporary test file name so real orders.json is never modified.
TEST_FILE = Path("test_orders.json")


# ---------------------------------------------------------
# Create sample test data
# ---------------------------------------------------------

def reset_test_data():
    sample_orders = [
        {
            "order_id": "O001",
            "customer_name": "Sample Customer A",
            "delivery_address": "123 Nathan Road, Kowloon",
            "created_at": "2026-11-10T09:00:00",
            "status": "Packed",
            "items": [],
            "total": "100.00",
            "delivery": {
                "delivery_method": None,
                "driver_id": None,
                "driver_name": None,
                "delivery_status": "Unassigned"
            },
            "status_history": [
                {"status": "Pending", "at": "2026-11-10T09:00:00"},
                {"status": "Packed", "at": "2026-11-10T09:30:00"}
            ]
        },
        {
            "order_id": "O002",
            "customer_name": "Sample Customer B",
            "delivery_address": "456 Queen's Road, Central",
            "created_at": "2026-11-10T10:00:00",
            "status": "Packed",
            "items": [],
            "total": "50.00",
            "delivery": {
                "delivery_method": None,
                "driver_id": None,
                "driver_name": None,
                "delivery_status": "Unassigned"
            },
            "status_history": [
                {"status": "Pending", "at": "2026-11-10T10:00:00"},
                {"status": "Packed", "at": "2026-11-10T10:15:00"}
            ]
        },
        {
            "order_id": "O003",
            "customer_name": "Sample Customer C",
            "delivery_address": "789 Hennessy Road, Wan Chai",
            "created_at": "2026-11-10T11:00:00",
            "status": "Pending",
            "items": [],
            "total": "80.00",
            "delivery": {
                "delivery_method": None,
                "driver_id": None,
                "driver_name": None,
                "delivery_status": "Unassigned"
            },
            "status_history": [
                {"status": "Pending", "at": "2026-11-10T11:00:00"}
            ]
        }
    ]
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_orders, f, indent=2)

# Initialize test data file.
reset_test_data()

# Store all test results for summary reporting.
results = []

def record(test_case, expected, actual, passed):
    status = "PASS" if passed else "FAIL"
    results.append((test_case, expected, actual, status))
    print("\n" + "-" * 60)
    print(f"Test Case      : {test_case}")
    print(f"Expected Result: {expected}")
    print(f"Actual Result  : {actual}")
    print(f"Result         : {status}")

print("=" * 60)
print("Increment 3 - Delivery & Tracking Testing & Validation")
print("=" * 60)

try:
    # ---------------------------------------------------------
    # Test 1 - View delivery details
    # ---------------------------------------------------------
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            delivery.view_delivery("O001",path=TEST_FILE)
        output = buf.getvalue()
        passed = ("Delivery Information" in output) and ("Unassigned" in output)
        record(
            "Test 1: View delivery details",
            "Correct delivery information displayed",
            "Delivery details displayed accurately",
            passed
        )
    except Exception as e:
        record("Test 1: View delivery details", "Correct delivery information displayed", str(e), False)

    # ---------------------------------------------------------
    # Test 2 - View order tracking
    # ---------------------------------------------------------
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            delivery.view_tracking("O001",path=TEST_FILE)
        output = buf.getvalue()
        passed = ("Order Tracking" in output) and ("Packed" in output) and ("Status History" in output)
        record(
            "Test 2: View order tracking",
            "Current status and status history displayed correctly",
            "Tracking status and history displayed",
            passed
        )
    except Exception as e:
        record("Test 2: View order tracking", "Current status and status history displayed correctly", str(e), False)

    # ---------------------------------------------------------
    # Test 3 - Assign Courier delivery
    # ---------------------------------------------------------
    try:
        buf = io.StringIO()
        with patch("builtins.input", side_effect=["1", "D001"]), redirect_stdout(buf):
            delivery.assign_delivery("O001",path=TEST_FILE)
        _, order = delivery.find_order("O001", TEST_FILE)
        passed = (
            order["delivery"]["delivery_method"] == "Courier"
            and order["delivery"]["driver_id"] == "D001"
            and order["delivery"]["driver_name"] == "Thomas"
            and order["delivery"]["delivery_status"] == "Assigned"
            and order["status"] == "Ready for Delivery"
        )
        record(
            "Test 3: Assign Courier delivery",
            "Delivery assigned successfully",
            f"Method={order['delivery']['delivery_method']}, Driver={order['delivery']['driver_id']}, OrderStatus={order['status']}",
            passed
        )
    except Exception as e:
        record("Test 3: Assign Courier delivery", "Delivery assigned successfully", str(e), False)

    # ---------------------------------------------------------
    # Test 4 - Assign Self Pickup delivery
    # ---------------------------------------------------------
    try:
        buf = io.StringIO()
        with patch("builtins.input", side_effect=["2"]), redirect_stdout(buf):
            delivery.assign_delivery("O002",path=TEST_FILE)
        _, order = delivery.find_order("O002", TEST_FILE)
        passed = (
            order["delivery"]["delivery_method"] == "Self Pickup"
            and order["delivery"]["driver_id"] is None
            and order["delivery"]["delivery_status"] == "Assigned"
            and order["status"] == "Ready for Delivery"
        )
        record(
            "Test 4: Assign Self Pickup delivery",
            "Delivery assigned successfully",
            f"Method={order['delivery']['delivery_method']}, Driver={order['delivery']['driver_id']}, OrderStatus={order['status']}",
            passed
        )
    except Exception as e:
        record("Test 4: Assign Self Pickup delivery", "Delivery assigned successfully", str(e), False)

    # ---------------------------------------------------------
    # Test 5 - Assign delivery to non-Packed order (Refusal)
    # ---------------------------------------------------------
    try:
        with patch("builtins.input", side_effect=["1", "D001"]):
            delivery.assign_delivery("O003",path=TEST_FILE)
        record("Test 5: Assign delivery to non-Packed order", "Rejected", "Allowed unexpectedly", False)
    except ValueError as e:
        record("Test 5: Assign delivery to non-Packed order", "Rejected", f"Rejected ({e})", True)

    # ---------------------------------------------------------
    # Test 6 - Assign Courier with invalid driver ID (Refusal)
    # ---------------------------------------------------------
    try:
        # Reset O002 to Packed for testing invalid driver
        orders = storage.load_orders(TEST_FILE)
        for o in orders:
            if o["order_id"] == "O002":
                o["status"] = "Packed"
                o["delivery"]["delivery_status"] = "Unassigned"
        storage.save_orders(orders, TEST_FILE)

        buf = io.StringIO()
        with patch("builtins.input", side_effect=["1", "D999"]), redirect_stdout(buf):
            delivery.assign_delivery("O002",path=TEST_FILE)
        record("Test 6: Assign Courier with invalid driver ID", "Rejected", "Allowed unexpectedly", False)
    except ValueError as e:
        record("Test 6: Assign Courier with invalid driver ID", "Rejected", f"Rejected ({e})", True)

    # ---------------------------------------------------------
    # Test 7 - Start delivery after assignment
    # ---------------------------------------------------------
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            delivery.start_delivery("O001",path=TEST_FILE)
        _, order = delivery.find_order("O001", TEST_FILE)
        passed = (
            order["delivery"]["delivery_status"] == "In Transit"
            and order["status"] == "Out for Delivery"
        )
        record(
            "Test 7: Start delivery after assignment",
            "Delivery Status becomes In Transit and Order Status becomes Out for Delivery",
            f"Delivery={order['delivery']['delivery_status']}, Order={order['status']}",
            passed
        )
    except Exception as e:
        record("Test 7: Start delivery after assignment", "Delivery Status becomes In Transit and Order Status becomes Out for Delivery", str(e), False)

    # ---------------------------------------------------------
    # Test 8 - Start delivery before assignment (Refusal)
    # ---------------------------------------------------------
    try:
        delivery.start_delivery("O002",path=TEST_FILE)
        record("Test 8: Start delivery before assignment", "Rejected", "Allowed unexpectedly", False)
    except ValueError as e:
        record("Test 8: Start delivery before assignment", "Rejected", f"Rejected ({e})", True)
# ---------------------------------------------------------
# Test 9 - Complete delivery successfully
# ---------------------------------------------------------
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            delivery.complete_delivery("O001",path=TEST_FILE)
        _, order = delivery.find_order("O001", TEST_FILE)
        passed = (
            order["delivery"]["delivery_status"] == "Delivered"
            and order["status"] == "Delivered"
        )
        record(
            "Test 9: Complete delivery successfully",
            "Delivery Status becomes Delivered and Order Status becomes Delivered",
            f"Delivery={order['delivery']['delivery_status']}, Order={order['status']}",
            passed
        )
    except Exception as e:
        record("Test 9: Complete delivery successfully", "Delivery Status becomes Delivered and Order Status becomes Delivered", str(e), False)
# ---------------------------------------------------------
# Test 10 - Complete delivery before In Transit (Refusal)
# ---------------------------------------------------------
    try:
        delivery.complete_delivery("O002",path=TEST_FILE)
        record("Test 10: Complete delivery before In Transit", "Rejected", "Allowed unexpectedly", False)
    except ValueError as e:
        record("Test 10: Complete delivery before In Transit", "Rejected", f"Rejected ({e})", True)
# ---------------------------------------------------------
# Test 11 - Reopen program (Data persistence after reload)
# ---------------------------------------------------------
    try:
        reloaded_orders = delivery.load_orders(TEST_FILE)
        o1_reloaded = next(o for o in reloaded_orders if o["order_id"] == "O001")
        passed = (
            o1_reloaded["delivery"]["delivery_status"] == "Delivered"
            and o1_reloaded["delivery"]["driver_id"] == "D001"
            and o1_reloaded["status"] == "Delivered"
        )
        record(
            "Test 11: Reopen program (Persistence check)",
            "Delivery information persists after reload",
            f"Reloaded DeliveryStatus={o1_reloaded['delivery']['delivery_status']}, Driver={o1_reloaded['delivery']['driver_id']}",
            passed
        )
    except Exception as e:
        record("Test 11: Reopen program (Persistence check)", "Delivery information persists after reload", str(e), False)
# ---------------------------------------------------------
# Test 12 - Invalid order ID (Refusal)
# ---------------------------------------------------------
    try:
        delivery.find_order("O999", TEST_FILE)
        record("Test 12: Invalid order ID", "Error displayed", "Order found unexpectedly", False)
    except ValueError as e:
        record("Test 12: Invalid order ID", "Error displayed", f"Error raised ({e})", True)
# ---------------------------------------------------------
# Test 13 - Delivery status history verification
# ---------------------------------------------------------
    try:
        _, order = delivery.find_order("O001", TEST_FILE)
        history_statuses = [entry["status"] for entry in order["status_history"]]
        expected_chain = ["Pending", "Packed", "Ready for Delivery", "Out for Delivery", "Delivered"]
        passed = (history_statuses == expected_chain)
        record(
            "Test 13: Delivery status history verification",
            "New status appended to status_history",
            f"History = {' -> '.join(history_statuses)}",
            passed
        )
    except Exception as e:
        record("Test 13: Delivery status history verification", "New status appended to status_history", str(e), False)
# ---------------------------------------------------------
# Test 14 - Delivery performance test (100 records < 2.0s)
# ---------------------------------------------------------
    try:
        perf_orders = []
        for i in range(1, 101):
            perf_orders.append({
                "order_id": f"O{i:03d}",
                "customer_name": f"Customer {i}",
                "delivery_address": "Sample Address",
                "created_at": "2026-11-10T09:00:00",
                "status": "Delivered",
                "items": [],
                "total": "50.00",
                "delivery": {
                    "delivery_method": "Courier",
                    "driver_id": "D001",
                    "driver_name": "Thomas",
                    "delivery_status": "Delivered"
                },
                "status_history": [{"status": "Delivered", "at": "2026-11-10T12:00:00"}]
            })
        delivery.save_orders(perf_orders, TEST_FILE)

        start_time = time.perf_counter()
        loaded = delivery.load_orders(TEST_FILE)
        elapsed = time.perf_counter() - start_time

        passed = (len(loaded) == 100) and (elapsed < 2.0)
        record(
            "Test 14: Delivery performance test",
            "Delivery record loaded successfully within performance target",
            f"Loaded {len(loaded)} records in {elapsed:.4f} s (target < 2.0 s)",
            passed
        )
    except Exception as e:
        record("Test 14: Delivery performance test", "Delivery record loaded successfully within performance target", str(e), False)

finally:
    # Restore original path and remove temporary file so real data is untouched
    
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

# ---------------------------------------------------------
# Print Final Summary (Fixed index check r[3] == "PASS")
# ---------------------------------------------------------
total_tests = len(results)
passed_tests = sum(1 for r in results if r[3] == "PASS")
failed_tests = total_tests - passed_tests
print("\n" + "=" * 60)
print(f"Summary: {passed_tests}/{total_tests} Passed, {failed_tests} Failed")
print("=" * 60)


