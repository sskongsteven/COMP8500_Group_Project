# =========================================================
# Unit Tests for order_menu.py (unittest)
# Prepared by Louis
# Purpose: Verify that the Order Menu Module
#          functions correctly using unittest.
# =========================================================

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import order as ord_core
import order_menu
from storage import save_orders, save_products


class TestOrderMenu(unittest.TestCase):
    # Tests for the E-Shop Order & Fulfillment menu workflow.

    def setUp(self):
        # Create temporary orders and products files and point order module to them.
        self.orders_file = Path("test_order_menu_orders.json")
        self.products_file = Path("test_order_menu_products.json")
        for p in (self.orders_file, self.products_file):
            if p.exists():
                p.unlink()

        save_products(
            [
                {
                    "product_id": "P001",
                    "product_name": "Notebook",
                    "price": "25.00",
                    "stock_quantity": 10,
                }
            ],
            path=self.products_file,
        )

        save_orders(
            [
                {
                    "order_id": "O001",
                    "customer_name": "Sample Customer A",
                    "delivery_address": "123 Test Street",
                    "created_at": "2026-10-27T10:30:00",
                    "status": "Pending",
                    "items": [
                        {
                            "product_id": "P001",
                            "product_name": "Notebook",
                            "price": "25.00",
                            "quantity": 2,
                            "line_total": "50.00",
                        }
                    ],
                    "total": "50.00",
                    "delivery": {
                        "delivery_method": "Courier",
                        "driver_id": None,
                        "driver_name": None,
                        "delivery_status": "Unassigned",
                    },
                    "status_history": [
                        {"status": "Pending", "at": "2026-10-27T10:30:00"}
                    ],
                }
            ],
            path=self.orders_file,
        )

        self.orig_list_orders = ord_core.list_orders
        self.orig_view_order_details = ord_core.view_order_details
        self.orig_pack_order = ord_core.pack_order
        self.orig_cancel_order = ord_core.cancel_order

        o_path = self.orders_file
        p_path = self.products_file
        ord_core.list_orders = lambda path=o_path: self.orig_list_orders(path=path)
        ord_core.view_order_details = lambda order_id, path=o_path: self.orig_view_order_details(
            order_id, path=path
        )
        ord_core.pack_order = lambda order_id, path=o_path, products_path=p_path: self.orig_pack_order(
            order_id, path=path, products_path=products_path
        )
        ord_core.cancel_order = lambda order_id, path=o_path: self.orig_cancel_order(
            order_id, path=path
        )

    def tearDown(self):
        # Restore original order functions and remove temporary test files.
        ord_core.list_orders = self.orig_list_orders
        ord_core.view_order_details = self.orig_view_order_details
        ord_core.pack_order = self.orig_pack_order
        ord_core.cancel_order = self.orig_cancel_order

        for p in (self.orders_file, self.products_file):
            if p.exists():
                p.unlink()

    def test_view_order_details_and_back_navigation(self):
        # View O001 details, decline viewing another, then exit.
        inputs = [
            "1",       # View Order Details
            "1",       # Select O001
            "n",       # Do not view another order
            "4",       # Return to Main Menu
        ]
        buf = io.StringIO()
        with (
            patch("order_menu.ord_core", ord_core),
            patch("builtins.input", side_effect=inputs),
            redirect_stdout(buf),
        ):
            order_menu.display_order_menu()

        output = buf.getvalue()
        self.assertIn("Order ID        : O001", output)
        self.assertIn("Sample Customer A", output)
        self.assertIn("Returning to main console loop.", output)

    def test_pack_order_and_reject_cancelling_packed_order(self):
        # Pack O001, then verify cancelling a Packed order is rejected.
        inputs = [
            "2", "1",  # Mark O001 as Packed
            "3", "1",  # Attempt to cancel Packed O001
            "4",       # Exit
        ]
        buf = io.StringIO()
        with (
            patch("order_menu.ord_core", ord_core),
            patch("builtins.input", side_effect=inputs),
            redirect_stdout(buf),
        ):
            order_menu.display_order_menu()

        output = buf.getvalue()
        self.assertIn("Order O001 status updated to: Packed", output)
        self.assertIn("Cancellation Refused:", output)

    def test_select_order_from_list_rollback_and_invalid_inputs(self):
        # Handle non-integer and out-of-range inputs, then return BACK on 0.
        inputs = ["abc", "99", "0"]
        buf = io.StringIO()
        with (
            patch("order_menu.ord_core", ord_core),
            patch("order_menu.ord_core.list_orders", return_value=[
                {
                    "order_id": "O001",
                    "customer_name": "Sample Customer A",
                    "status": "Pending",
                    "total": "50.00",
                }
            ]),
            patch("builtins.input", side_effect=inputs),
            redirect_stdout(buf),
        ):
            result = order_menu.select_order_from_list()

        self.assertEqual(result, "BACK")
        self.assertIn("must be valid numerical integers", buf.getvalue())
        self.assertIn("must be bounded between 0 and 1", buf.getvalue())


if __name__ == "__main__":
    print("=" * 60)
    print("Unit Tests for order_menu.py (unittest)")
    print("=" * 60)
    unittest.main(verbosity=2)
