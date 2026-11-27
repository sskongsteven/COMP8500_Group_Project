# =========================================================
# Unit Tests for web_app.py (unittest)
# Prepared by Louis
# Purpose: Verify that the Web Display & API Module
#          functions correctly using unittest.
# =========================================================

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import common
import storage
import web_app


class TestWebApp(unittest.TestCase):
    # Unit tests for web_app.py HTTP routes, API endpoints, and state isolation.

    def setUp(self):
        # Create temporary JSON files and start a local test HTTP server.
        self.products_file = Path("test_web_app_products.json")
        self.orders_file = Path("test_web_app_orders.json")

        for path in (self.products_file, self.orders_file):
            if path.exists():
                path.unlink()

        self.initial_products = [
            {
                "product_id": "P001",
                "product_name": "Notebook",
                "price": "25.00",
                "stock_quantity": 10,
            }
        ]
        self.initial_orders = [
            {
                "order_id": "O001",
                "customer_name": "Customer A",
                "delivery_address": "123 Nathan Road",
                "created_at": "2026-11-10T09:00:00",
                "status": common.STATUS_PENDING,
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
                "delivery": common.new_delivery(),
                "status_history": [
                    common.new_status_history_entry(
                        common.STATUS_PENDING, "2026-11-10T09:00:00"
                    )
                ],
            }
        ]

        orig_load_products = storage.load_products
        orig_save_products = storage.save_products
        orig_load_orders = storage.load_orders
        orig_save_orders = storage.save_orders

        orig_load_products(self.initial_products if False else self.products_file) if False else None
        with self.products_file.open("w", encoding="utf-8") as f:
            json.dump(self.initial_products, f, indent=2)
        with self.orders_file.open("w", encoding="utf-8") as f:
            json.dump(self.initial_orders, f, indent=2)

        p_file = self.products_file
        o_file = self.orders_file

        # Force all storage reads/writes to target the temporary test files.
        self.patches = [
            patch.object(storage, "PRODUCTS_FILE", p_file),
            patch.object(storage, "ORDERS_FILE", o_file),
            patch.object(
                storage,
                "load_products",
                side_effect=lambda path=p_file: orig_load_products(p_file),
            ),
            patch.object(
                storage,
                "save_products",
                side_effect=lambda products, path=p_file: orig_save_products(products, p_file),
            ),
            patch.object(
                storage,
                "load_orders",
                side_effect=lambda path=o_file: orig_load_orders(o_file),
            ),
            patch.object(
                storage,
                "save_orders",
                side_effect=lambda orders, path=o_file: orig_save_orders(orders, o_file),
            ),
        ]
        for p in self.patches:
            p.start()

        # Also rebind default path arguments on core functions if they use keyword defaults.
        self._saved_defaults = []
        for fn, new_defs in [
            (web_app.inventory.list_products, (p_file,)),
            (web_app.inventory.add_product, (p_file,)),
            (web_app.inventory.update_product, (None, None, p_file)),
            (web_app.inventory.change_stock, (p_file,)),
            (web_app.order.list_orders, (o_file,)),
            (web_app.order.view_order_details, (o_file,)),
            (web_app.order.pack_order, (o_file, p_file)),
            (web_app.order.cancel_order, (o_file,)),
            (web_app.delivery.find_order, (o_file,)),
            (web_app.delivery.start_delivery, (o_file,)),
            (web_app.delivery.complete_delivery, (o_file,)),
        ]:
            if hasattr(fn, "__defaults__"):
                self._saved_defaults.append((fn, fn.__defaults__))
                if fn.__defaults__ and len(fn.__defaults__) >= len(new_defs):
                    fn.__defaults__ = fn.__defaults__[:-len(new_defs)] + new_defs

        web_app.capture_initial_snapshot()

        # Start ThreadingHTTPServer on port 0 (OS assigns an available ephemeral port).
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), web_app.LogisticsHandler)
        self.port = self.server.server_address[1]
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.server_thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.server_thread.start()

    def tearDown(self):
        # Shut down test server, restore defaults/patches, and delete temporary JSON files.
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join(timeout=2)

        for fn, old_defs in self._saved_defaults:
            fn.__defaults__ = old_defs

        for p in reversed(self.patches):
            p.stop()

        for path in (self.products_file, self.orders_file):
            if path.exists():
                path.unlink()

    def _request_json(self, path, method="GET", payload=None):
        # Send an HTTP request and return (status_code, parsed_json_dict).
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if payload is not None else {}
        req = Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        try:
            with urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except HTTPError as err:
            return err.code, json.loads(err.read().decode("utf-8"))

    def test_01_get_index_html_and_state(self):
        # Verify GET / serves the HTML dashboard and GET /api/state returns datasets.
        with urlopen(f"{self.base_url}/") as resp:
            html = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("E-Shop Logistics Management System", html)

        status, state = self._request_json("/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(len(state["products"]), 1)
        self.assertEqual(len(state["orders"]), 1)
        self.assertIn("D001", state["drivers"])

    def test_02_product_crud_and_stock_adjustment(self):
        # Verify adding, updating, and adjusting stock for products via API.
        status, created = self._request_json(
            "/api/products",
            method="POST",
            payload={"name": "Wireless Mouse", "price": "120.00", "starting_stock": 15},
        )
        self.assertEqual(status, 201)
        self.assertEqual(created["product"]["product_id"], "P002")

        status, updated = self._request_json(
            "/api/products/P002",
            method="PUT",
            payload={"name": "Ergonomic Mouse", "price": "135.00"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(updated["product"]["product_name"], "Ergonomic Mouse")

        status, stocked = self._request_json(
            "/api/products/P002/stock",
            method="POST",
            payload={"change": 5},
        )
        self.assertEqual(status, 200)
        self.assertEqual(stocked["product"]["stock_quantity"], 20)

    def test_03_end_to_end_order_and_delivery_lifecycle(self):
        # Verify packing, assigning Courier delivery, starting, and completing an order.
        status, packed = self._request_json("/api/orders/O001/pack", method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(packed["order"]["status"], common.STATUS_PACKED)

        # Stock of P001 should drop from 10 to 8 after packing 2 units.
        _, state = self._request_json("/api/state")
        self.assertEqual(state["products"][0]["stock_quantity"], 8)

        status, assigned = self._request_json(
            "/api/orders/O001/delivery/assign",
            method="POST",
            payload={
                "delivery_method": common.DELIVERY_METHOD_COURIER,
                "driver_id": "D001",
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(assigned["order"]["status"], common.STATUS_READY_FOR_DELIVERY)
        self.assertEqual(assigned["order"]["delivery"]["driver_name"], "Thomas")

        status, started = self._request_json(
            "/api/orders/O001/delivery/start", method="POST"
        )
        self.assertEqual(status, 200)
        self.assertEqual(started["order"]["status"], common.STATUS_OUT_FOR_DELIVERY)

        status, completed = self._request_json(
            "/api/orders/O001/delivery/complete", method="POST"
        )
        self.assertEqual(status, 200)
        self.assertEqual(completed["order"]["status"], common.STATUS_DELIVERED)

    def test_04_cancel_order_and_validation_errors(self):
        # Verify cancelling a Pending order works and invalid transitions return HTTP 400.
        status, cancelled = self._request_json("/api/orders/O001/cancel", method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(cancelled["order"]["status"], common.STATUS_CANCELLED)

        # Packing an already Cancelled order must fail with 400 Bad Request.
        status, err = self._request_json("/api/orders/O001/pack", method="POST")
        self.assertEqual(status, 400)
        self.assertIn("error", err)

        # Unknown route must return 404 Not Found.
        status, err = self._request_json("/api/unknown")
        self.assertEqual(status, 404)
        self.assertEqual(err["error"], "Not found")

    def test_05_reset_demo_restores_initial_snapshot(self):
        # Verify POST /api/reset restores the starting products and orders snapshot.
        self._request_json("/api/orders/O001/pack", method="POST")
        self._request_json(
            "/api/products",
            method="POST",
            payload={"name": "Temp Item", "price": "10.00", "starting_stock": 5},
        )

        status, reset_res = self._request_json("/api/reset", method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(reset_res["status"], "reset")

        _, state = self._request_json("/api/state")
        self.assertEqual(len(state["products"]), 1)
        self.assertEqual(state["products"][0]["stock_quantity"], 10)
        self.assertEqual(state["orders"][0]["status"], common.STATUS_PENDING)


if __name__ == "__main__":
    print("=" * 60)
    print("Unit Tests for web_app.py (unittest)")
    print("=" * 60)
    unittest.main(verbosity=2)
