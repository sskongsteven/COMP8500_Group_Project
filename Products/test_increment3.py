import io
import json
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from common import (
    DELIVERY_METHOD_COURIER,
    DELIVERY_METHOD_SELF_PICKUP,
    DELIVERY_STATUS_ASSIGNED,
    DELIVERY_STATUS_DELIVERED,
    DELIVERY_STATUS_IN_TRANSIT,
    DELIVERY_STATUS_UNASSIGNED,
    STATUS_DELIVERED,
    STATUS_OUT_FOR_DELIVERY,
    STATUS_PACKED,
    STATUS_PENDING,
    STATUS_READY_FOR_DELIVERY,
    new_delivery,
    new_status_history_entry,
)
from delivery import (
    assign_delivery,
    complete_delivery,
    find_order,
    start_delivery,
    view_delivery,
    view_tracking,
)
from storage import load_orders, save_orders

class TestIncrement3Delivery(unittest.TestCase):
    # Unit tests for the Delivery & Tracking Module.

    def setUp(self):
        # Create a clean temporary orders file with sample data before each test.
        self.orders_file = Path("test_orders_inc3_unittest.json")
        self.sample_orders = [
            {
                "order_id": "O001",
                "customer_name": "Customer A",
                "delivery_address": "123 Nathan Road",
                "created_at": "2026-11-10T09:00:00",
                "status": STATUS_PACKED,
                "items": [],
                "total": "100.00",
                "delivery": new_delivery(),
                "status_history": [
                    new_status_history_entry(STATUS_PENDING, "2026-11-10T09:00:00"),
                    new_status_history_entry(STATUS_PACKED, "2026-11-10T09:30:00"),
                ],
            },
            {
                "order_id": "O002",
                "customer_name": "Customer B",
                "delivery_address": "456 Queen's Road",
                "created_at": "2026-11-10T10:00:00",
                "status": STATUS_PENDING,
                "items": [],
                "total": "50.00",
                "delivery": new_delivery(),
                "status_history": [
                    new_status_history_entry(STATUS_PENDING, "2026-11-10T10:00:00"),
                ],
            },
        ]

        save_orders(self.sample_orders, self.orders_file)

    def tearDown(self):
        # Remove temporary test file after each test.
        if self.orders_file.exists():
            self.orders_file.unlink()
    
    def test_01_view_delivery_details(self):
        # Verify delivery details are displayed accurately for a valid order.
        buf = io.StringIO()
        with redirect_stdout(buf):
            view_delivery("O001", path=self.orders_file)
        output = buf.getvalue()
        self.assertIn("Delivery Information", output)
        self.assertIn("Unassigned", output)

    def test_02_view_order_tracking(self):
            # Verify current status and status history are displayed correctly.
            buf = io.StringIO()
            with redirect_stdout(buf):
                view_tracking("O001", path=self.orders_file)
            output = buf.getvalue()
            self.assertIn("Order Tracking", output)
            self.assertIn(STATUS_PACKED, output)
            self.assertIn("Status History", output)

    def test_03_assign_courier_delivery(self):
        # Verify assigning Courier delivery with driver choice 1 (D001 - Thomas).
        buf = io.StringIO()
        with patch("builtins.input", side_effect=["1", "1"]), redirect_stdout(buf):
            assign_delivery("O001", path=self.orders_file)
        _, order = find_order("O001", self.orders_file)
        self.assertEqual(order["delivery"]["delivery_method"], DELIVERY_METHOD_COURIER)
        self.assertEqual(order["delivery"]["driver_id"], "D001")
        self.assertEqual(order["delivery"]["driver_name"], "Thomas")
        self.assertEqual(order["delivery"]["delivery_status"], DELIVERY_STATUS_ASSIGNED)
        self.assertEqual(order["status"], STATUS_READY_FOR_DELIVERY)

    def test_04_assign_self_pickup_delivery(self):
        # Verify assigning Self Pickup delivery without a driver.
        buf = io.StringIO()
        with patch("builtins.input", side_effect=["2"]), redirect_stdout(buf):
            assign_delivery("O001", path=self.orders_file)
        _, order = find_order("O001", self.orders_file)
        self.assertEqual(order["delivery"]["delivery_method"], DELIVERY_METHOD_SELF_PICKUP)
        self.assertIsNone(order["delivery"]["driver_id"])
        self.assertEqual(order["delivery"]["delivery_status"], DELIVERY_STATUS_ASSIGNED)
        self.assertEqual(order["status"], STATUS_READY_FOR_DELIVERY)

    def test_05_reject_assign_non_packed_order(self):
            # Reject delivery assignment when order status is not Packed (O002 is Pending).
            with patch("builtins.input", side_effect=["1", "1"]):
                with self.assertRaises(ValueError):
                    assign_delivery("O002", path=self.orders_file)

    def test_06_reject_invalid_driver_selection(self):
        # Reject Courier delivery when an invalid driver number is entered.
        buf = io.StringIO()
        with patch("builtins.input", side_effect=["1", "99"]), redirect_stdout(buf):
            with self.assertRaises(ValueError):
                assign_delivery("O001", path=self.orders_file)

    def test_07_start_delivery_after_assignment(self):
        # Verify starting an Assigned delivery updates statuses to In Transit and Out for Delivery.
        buf = io.StringIO()
        with patch("builtins.input", side_effect=["1", "1"]), redirect_stdout(buf):
            assign_delivery("O001", path=self.orders_file)
        with redirect_stdout(buf):
            start_delivery("O001", path=self.orders_file)
        _, order = find_order("O001", self.orders_file)
        self.assertEqual(order["delivery"]["delivery_status"], DELIVERY_STATUS_IN_TRANSIT)
        self.assertEqual(order["status"], STATUS_OUT_FOR_DELIVERY)

    def test_08_reject_start_delivery_before_assignment(self):
        # Reject starting delivery when delivery status is still Unassigned.
        with self.assertRaises(ValueError):
            start_delivery("O001", path=self.orders_file)

    def test_09_complete_delivery_successfully(self):
            # Verify completing an In Transit delivery updates both statuses to Delivered.
            buf = io.StringIO()
            with patch("builtins.input", side_effect=["1", "1"]), redirect_stdout(buf):
                assign_delivery("O001", path=self.orders_file)
            with redirect_stdout(buf):
                start_delivery("O001", path=self.orders_file)
                complete_delivery("O001", path=self.orders_file)
            _, order = find_order("O001", self.orders_file)
            self.assertEqual(order["delivery"]["delivery_status"], DELIVERY_STATUS_DELIVERED)
            self.assertEqual(order["status"], STATUS_DELIVERED)
    
    def test_10_reject_complete_delivery_before_in_transit(self):
        # Reject completing delivery when delivery status is not In Transit.
        with self.assertRaises(ValueError):
            complete_delivery("O001", path=self.orders_file)

    def test_11_reopen_program_persistence(self):
        # Verify updated delivery details persist after reloading from disk.
        buf = io.StringIO()
        with patch("builtins.input", side_effect=["1", "1"]), redirect_stdout(buf):
            assign_delivery("O001", path=self.orders_file)
        reloaded_orders = load_orders(self.orders_file)
        o1_reloaded = next(o for o in reloaded_orders if o["order_id"] == "O001")
        self.assertEqual(o1_reloaded["delivery"]["delivery_status"], DELIVERY_STATUS_ASSIGNED)
        self.assertEqual(o1_reloaded["delivery"]["driver_id"], "D001")

    def test_12_reject_invalid_order_id(self):
            # Raise ValueError when querying a non-existing order ID.
            with self.assertRaises(ValueError):
                find_order("O999", self.orders_file)

    def test_13_delivery_status_history_verification(self):
        # Verify each delivery transition appends a new status entry to status_history.
        buf = io.StringIO()
        with patch("builtins.input", side_effect=["1", "1"]), redirect_stdout(buf):
            assign_delivery("O001", path=self.orders_file)
        with redirect_stdout(buf):
            start_delivery("O001", path=self.orders_file)
            complete_delivery("O001", path=self.orders_file)
        _, order = find_order("O001", self.orders_file)
        history_statuses = [entry["status"] for entry in order["status_history"]]
        expected_chain = [
            STATUS_PENDING,
            STATUS_PACKED,
            STATUS_READY_FOR_DELIVERY,
            STATUS_OUT_FOR_DELIVERY,
            STATUS_DELIVERED,
        ]
        self.assertEqual(history_statuses, expected_chain)

    def test_14_performance_load_100_delivery_orders(self):
        # Verify loading 100 delivery records takes less than 2.0 seconds.
        perf_orders = [
            {
                "order_id": f"O{i:03}",
                "customer_name": f"Customer {i}",
                "delivery_address": "Sample Address",
                "created_at": "2026-11-10T09:00:00",
                "status": STATUS_DELIVERED,
                "items": [],
                "total": "50.00",
                "delivery": {
                    "delivery_method": DELIVERY_METHOD_COURIER,
                    "driver_id": "D001",
                    "driver_name": "Thomas",
                    "delivery_status": DELIVERY_STATUS_DELIVERED,
                },
                "status_history": [
                    new_status_history_entry(STATUS_DELIVERED, "2026-11-10T12:00:00")
                ],
            }
            for i in range(1, 101)
        ]
        with self.orders_file.open("w", encoding="utf-8") as f:
            json.dump(perf_orders, f, indent=2)

        start = time.perf_counter()
        loaded = load_orders(self.orders_file)
        duration = time.perf_counter() - start

        print(f"\n    [Timing] Loaded {len(loaded)} orders in {duration:.4f}s")
        self.assertEqual(len(loaded), 100)
        self.assertLess(duration, 2.0)


if __name__ == "__main__":
    print("=" * 60)
    print("Increment 3 - Testing & Validation (unittest)")
    print("=" * 60)
    unittest.main(verbosity=2)
