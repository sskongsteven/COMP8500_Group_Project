import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import delivery as del_core
import delivery_menu
from common import STATUS_PACKED, STATUS_PENDING, new_delivery, new_status_history_entry
from storage import load_orders, save_orders


class TestDeliveryMenu(unittest.TestCase):
    # Tests for the E-Shop Delivery & Tracking menu workflow.

    def setUp(self):
        # Create temporary orders file and redirect delivery functions to it.
        self.orders_file = Path("test_delivery_menu_orders.json")
        if self.orders_file.exists():
            self.orders_file.unlink()

        save_orders(
            [
                {
                    "order_id": "O001",
                    "customer_name": "Sample Customer A",
                    "delivery_address": "123 Test Street",
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
                    "customer_name": "Sample Customer B",
                    "delivery_address": "456 Test Road",
                    "created_at": "2026-11-10T10:00:00",
                    "status": STATUS_PENDING,
                    "items": [],
                    "total": "50.00",
                    "delivery": new_delivery(),
                    "status_history": [
                        new_status_history_entry(STATUS_PENDING, "2026-11-10T10:00:00"),
                    ],
                },
            ],
            path=self.orders_file,
        )
        self.orig_load_orders = del_core.load_orders
        self.orig_view_delivery = del_core.view_delivery
        self.orig_assign_delivery = del_core.assign_delivery
        self.orig_start_delivery = del_core.start_delivery
        self.orig_complete_delivery = del_core.complete_delivery
        self.orig_view_tracking = del_core.view_tracking

        o_path = self.orders_file
        del_core.load_orders = lambda path=o_path: self.orig_load_orders(path=path)
        del_core.view_delivery = lambda order_id, path=o_path: self.orig_view_delivery(order_id, path=path)
        del_core.assign_delivery = lambda order_id, path=o_path: self.orig_assign_delivery(order_id, path=path)
        del_core.start_delivery = lambda order_id, path=o_path: self.orig_start_delivery(order_id, path=path)
        del_core.complete_delivery = lambda order_id, path=o_path: self.orig_complete_delivery(order_id, path=path)
        del_core.view_tracking = lambda order_id, path=o_path: self.orig_view_tracking(order_id, path=path)

    def tearDown(self):
        # Restore original delivery functions and remove temporary test file.
        del_core.load_orders = self.orig_load_orders
        del_core.view_delivery = self.orig_view_delivery
        del_core.assign_delivery = self.orig_assign_delivery
        del_core.start_delivery = self.orig_start_delivery
        del_core.complete_delivery = self.orig_complete_delivery
        del_core.view_tracking = self.orig_view_tracking

        if self.orders_file.exists():
            self.orders_file.unlink()

    def test_01_view_delivery_details_and_back_navigation(self):
        # View O001 delivery details, decline viewing another, then exit menu.
        inputs = ["1", "1", "n", "6"]
        buf = io.StringIO()
        with (
            patch("delivery_menu.del_core", del_core),
            patch("builtins.input", side_effect=inputs),
            redirect_stdout(buf),
        ):
            delivery_menu.display_delivery_menu()

        output = buf.getvalue()
        self.assertIn("Delivery Information", output)
        self.assertIn("Unassigned", output)
        self.assertIn("Returning to main console loop.", output)

    def test_02_full_delivery_workflow_and_tracking(self):
            # Assign Courier (driver 1), start delivery, complete delivery, and view tracking for O001.
            inputs = [
                "2", "1", "1", "1",  # Assign Delivery -> O001 -> Courier -> Driver 1 (D001)
                "3", "1",            # Start Delivery -> O001
                "4", "1",            # Complete Delivery -> O001
                "5", "1",            # View Order Tracking -> O001
                "6",                 # Return to Main Menu
            ]
            buf = io.StringIO()
            with (
                patch("delivery_menu.del_core", del_core),
                patch("builtins.input", side_effect=inputs),
                redirect_stdout(buf),
            ):
                delivery_menu.display_delivery_menu()
    
            output = buf.getvalue()
            self.assertIn("Delivery assigned successfully.", output)
            self.assertIn("Delivery started successfully.", output)
            self.assertIn("Delivery completed successfully.", output)
            self.assertIn("Order Status : Delivered", output)

    def test_03_reject_assigning_pending_order(self):
        # Attempt to assign delivery to Pending order O002 and verify rejection.
        inputs = [
            "2", "2",  # Assign Delivery -> select row 2 (O002, Pending)
            "6",       # Return to Main Menu
        ]
        buf = io.StringIO()
        with (
            patch("delivery_menu.del_core", del_core),
            patch("builtins.input", side_effect=inputs),
            redirect_stdout(buf),
        ):
            delivery_menu.display_delivery_menu()

        self.assertIn("Assignment Rejected: Only Packed orders can be assigned.", buf.getvalue())

    def test_04_select_order_from_list_rollback_and_invalid_inputs(self):
        # Handle non-integer and out-of-range inputs, then return BACK on 0.
        inputs = ["abc", "99", "0"]
        buf = io.StringIO()
        with (
            patch("delivery_menu.del_core", del_core),
            patch("builtins.input", side_effect=inputs),
            redirect_stdout(buf),
        ):
            result = delivery_menu.select_order_from_list()

        self.assertEqual(result, "BACK")
        self.assertIn("must be valid numerical integers", buf.getvalue())
        self.assertIn("must be bounded between 0 and 2", buf.getvalue())


if __name__ == "__main__":
    print("=" * 60)
    print("Unit Tests for delivery_menu.py (unittest)")
    print("=" * 60)
    unittest.main(verbosity=2)
