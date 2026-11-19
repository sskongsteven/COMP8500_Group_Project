# =========================================================
# Increment 2 - Testing & Validation (unittest)
# Prepared by Louis
# Purpose: Verify that the Order & Fulfilment Module
#          functions correctly using unittest.
# =========================================================

import json
import time
import unittest
from pathlib import Path

from common import (
    STATUS_CANCELLED,
    STATUS_DELIVERED,
    STATUS_OUT_FOR_DELIVERY,
    STATUS_PACKED,
    STATUS_PENDING,
    STATUS_READY_FOR_DELIVERY,
    new_status_history_entry,
)
from inventory import load_products
from order import (
    cancel_order,
    list_orders,
    pack_order,
    view_order_details,
)
from storage import load_orders, save_orders


class TestIncrement2Order(unittest.TestCase):
    # Unit tests for the Order & Fulfilment Module.

    def setUp(self):
        # Create clean temporary orders and products files before each test.
        self.orders_file = Path("test_orders_unittest.json")
        self.products_file = Path("test_products_unittest.json")

        self.sample_orders = [
            {
                "order_id": "O001",
                "customer_name": "Customer A",
                "delivery_address": "Test Address",
                "created_at": "2026-10-27T10:30:00",
                "status": STATUS_PENDING,
                "items": [
                    {
                        "product_id": "P001",
                        "product_name": "Notebook",
                        "price": "25.00",
                        "quantity": 2,
                        "line_total": "50.00",
                    }
                ],
                "total": "100.00",
                "delivery": None,
                "status_history": [
                    {"status": STATUS_PENDING, "at": "2026-10-27T10:30:00"}
                ],
            }
        ]

        self.sample_products = [
            {
                "product_id": "P001",
                "product_name": "Notebook",
                "price": "25.00",
                "stock_quantity": 10,
            }
        ]

        self._write_sample_data()

    def tearDown(self):
        # Remove temporary test files after each test.
        if self.orders_file.exists():
            self.orders_file.unlink()
        if self.products_file.exists():
            self.products_file.unlink()

    def _write_sample_data(self):
        # Write sample orders and products to their temporary files.
        with self.orders_file.open("w", encoding="utf-8") as f:
            json.dump(self.sample_orders, f, indent=2)
        with self.products_file.open("w", encoding="utf-8") as f:
            json.dump(self.sample_products, f, indent=2)

    def _set_order_status(self, order_id, new_status, timestamp="2026-10-27T11:00:00"):
        # Helper to advance an order's status for testing downstream guards.
        orders = load_orders(self.orders_file)
        for order in orders:
            if order["order_id"] == order_id:
                order["status"] = new_status
                order["status_history"].append(
                    new_status_history_entry(new_status, timestamp)
                )
        save_orders(orders, self.orders_file)

    def test_01_list_all_orders(self):
        # Verify all saved orders are returned.
        orders = list_orders(path=self.orders_file)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["order_id"], "O001")

    def test_02_view_order_details(self):
        # Verify order details are retrieved for a valid order ID.
        order = view_order_details("O001", path=self.orders_file)
        self.assertEqual(order["order_id"], "O001")
        self.assertEqual(order["customer_name"], "Customer A")

    def test_03_mark_order_as_packed(self):
        # Verify packing a Pending order updates its status to Packed.
        order = pack_order(
            "O001",
            path=self.orders_file,
            products_path=self.products_file,
        )
        self.assertEqual(order["status"], STATUS_PACKED)

    def test_04_cancel_pending_order(self):
        # Verify cancelling a Pending order changes its status to Cancelled.
        order = cancel_order("O001", path=self.orders_file)
        self.assertEqual(order["status"], STATUS_CANCELLED)

    def test_05_cancel_packed_order_rejected(self):
        # Reject cancelling an order once it is Packed.
        pack_order(
            "O001",
            path=self.orders_file,
            products_path=self.products_file,
        )
        with self.assertRaises(ValueError):
            cancel_order("O001", path=self.orders_file)

    def test_06_non_existing_order_rejected(self):
        # Raise ValueError when viewing a non-existing order ID.
        with self.assertRaises(ValueError):
            view_order_details("O999", path=self.orders_file)

    def test_07_reopen_program_persistence(self):
        # Verify updated order status persists after reloading from disk.
        pack_order(
            "O001",
            path=self.orders_file,
            products_path=self.products_file,
        )
        reloaded_order = view_order_details("O001", path=self.orders_file)
        self.assertEqual(reloaded_order["status"], STATUS_PACKED)

    def test_08_cannot_pack_ready_for_delivery_order(self):
        # Reject packing an order that is already Ready for Delivery.
        self._set_order_status("O001", STATUS_READY_FOR_DELIVERY)
        with self.assertRaises(ValueError):
            pack_order(
                "O001",
                path=self.orders_file,
                products_path=self.products_file,
            )

    def test_09_cannot_pack_out_for_delivery_order(self):
        # Reject packing an order that is Out for Delivery.
        self._set_order_status("O001", STATUS_OUT_FOR_DELIVERY)
        with self.assertRaises(ValueError):
            pack_order(
                "O001",
                path=self.orders_file,
                products_path=self.products_file,
            )

    def test_10_cannot_pack_delivered_order(self):
        # Reject packing an order that is already Delivered.
        self._set_order_status("O001", STATUS_DELIVERED)
        with self.assertRaises(ValueError):
            pack_order(
                "O001",
                path=self.orders_file,
                products_path=self.products_file,
            )

    def test_11_cannot_cancel_ready_for_delivery_order(self):
        # Reject cancelling an order that is Ready for Delivery.
        self._set_order_status("O001", STATUS_READY_FOR_DELIVERY)
        with self.assertRaises(ValueError):
            cancel_order("O001", path=self.orders_file)

    def test_12_cannot_cancel_out_for_delivery_order(self):
        # Reject cancelling an order that is Out for Delivery.
        self._set_order_status("O001", STATUS_OUT_FOR_DELIVERY)
        with self.assertRaises(ValueError):
            cancel_order("O001", path=self.orders_file)

    def test_13_cannot_cancel_delivered_order(self):
        # Reject cancelling an order that is already Delivered.
        self._set_order_status("O001", STATUS_DELIVERED)
        with self.assertRaises(ValueError):
            cancel_order("O001", path=self.orders_file)

    def test_14_status_history_updated_on_pack(self):
        # Verify packing appends a new Packed entry to status_history.
        order = pack_order(
            "O001",
            path=self.orders_file,
            products_path=self.products_file,
        )
        self.assertEqual(order["status_history"][-1]["status"], STATUS_PACKED)
        self.assertEqual(len(order["status_history"]), 2)

    def test_15_empty_order_file(self):
        # Verify loading an empty order list returns zero orders.
        with self.orders_file.open("w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

        orders = load_orders(path=self.orders_file)
        self.assertEqual(len(orders), 0)

    def test_16_performance_load_100_orders(self):
        # Verify loading 100 orders takes less than 2 seconds.
        performance_orders = [
            {
                "order_id": f"O{i:03}",
                "customer_name": f"Customer {i}",
                "delivery_address": "Test Address",
                "created_at": "2026-10-27T10:30:00",
                "status": STATUS_PENDING,
                "items": [],
                "total": "100.00",
                "delivery": None,
                "status_history": [
                    {"status": STATUS_PENDING, "at": "2026-10-27T10:30:00"}
                ],
            }
            for i in range(1, 101)
        ]
        save_orders(performance_orders, self.orders_file)

        start = time.perf_counter()
        orders = load_orders(path=self.orders_file)
        duration = time.perf_counter() - start

        print(f"\n    [Timing] Loaded {len(orders)} orders in {duration:.4f}s")
        self.assertEqual(len(orders), 100)
        self.assertLess(duration, 2.0)

    def test_17_pack_order_deducts_stock(self):
        # Verify packing O001 deducts 2 units of P001 (10 -> 8).
        pack_order(
            "O001",
            path=self.orders_file,
            products_path=self.products_file,
        )
        products = load_products(self.products_file)
        self.assertEqual(products[0]["stock_quantity"], 8)

    def test_18_pack_order_insufficient_stock_rejected(self):
        # Reject packing when available stock is lower than required quantity.
        self.sample_products[0]["stock_quantity"] = 1
        self._write_sample_data()

        with self.assertRaises(ValueError):
            pack_order(
                "O001",
                path=self.orders_file,
                products_path=self.products_file,
            )

    def test_19_pack_same_order_twice_rejected(self):
        # Reject packing an order a second time after it is already Packed.
        pack_order(
            "O001",
            path=self.orders_file,
            products_path=self.products_file,
        )
        with self.assertRaises(ValueError):
            pack_order(
                "O001",
                path=self.orders_file,
                products_path=self.products_file,
            )


if __name__ == "__main__":
    print("=" * 60)
    print("Increment 2 - Testing & Validation (unittest)")
    print("=" * 60)
    unittest.main(verbosity=2)
