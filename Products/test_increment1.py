# =========================================================
# Increment 1 - Testing & Validation (unittest)
# Prepared by Louis
# Purpose: Verify that the Product & Inventory Module
#          functions correctly using unittest.
# =========================================================

import time
import unittest
from pathlib import Path

from inventory import (
    add_product,
    change_stock,
    check_availability,
    list_products,
    update_product,
)


class TestIncrement1Inventory(unittest.TestCase):
    # Unit tests for the Product & Inventory Module.

    def setUp(self):
        # Create a clean temporary products JSON file before each test.
        self.test_file = Path("test_products_unittest.json")
        if self.test_file.exists():
            self.test_file.unlink()

    def tearDown(self):
        # Remove the temporary products JSON file after each test.
        if self.test_file.exists():
            self.test_file.unlink()

    def test_01_add_valid_product(self):
        # Add a valid product and verify it receives an ID and persists.
        product = add_product(
            "Testing Product",
            "12.50",
            20,
            path=self.test_file,
        )
        products = list_products(path=self.test_file)

        self.assertTrue(bool(product["product_id"]))
        self.assertEqual(product["product_name"], "Testing Product")
        self.assertEqual(product["price"], "12.50")
        self.assertEqual(product["stock_quantity"], 20)
        self.assertTrue(any(p["product_id"] == product["product_id"] for p in products))

    def test_02_add_product_empty_name_rejected(self):
        # Reject a product with an empty or whitespace-only name.
        with self.assertRaises(ValueError):
            add_product(
                "",
                "12.50",
                20,
                path=self.test_file,
            )

        self.assertEqual(list_products(path=self.test_file), [])

    def test_03_add_product_negative_price_rejected(self):
        # Reject a product with a negative price.
        with self.assertRaises(ValueError):
            add_product(
                "Negative Price Product",
                "-5.00",
                20,
                path=self.test_file,
            )

        self.assertEqual(list_products(path=self.test_file), [])

    def test_04_add_product_negative_starting_stock_rejected(self):
        # Reject a product with negative starting stock.
        with self.assertRaises(ValueError):
            add_product(
                "Negative Stock Product",
                "12.50",
                -10,
                path=self.test_file,
            )

        self.assertEqual(list_products(path=self.test_file), [])

    def test_05_update_product_information(self):
        # Update an existing product's name and price.
        product = add_product(
            "Testing Product",
            "12.50",
            20,
            path=self.test_file,
        )

        updated = update_product(
            product["product_id"],
            name="Updated Testing Product",
            price="15.00",
            path=self.test_file,
        )

        self.assertEqual(updated["product_name"], "Updated Testing Product")
        self.assertEqual(updated["price"], "15.00")

    def test_06_add_stock(self):
        # Increase stock quantity when given a positive adjustment.
        product = add_product(
            "Testing Product",
            "12.50",
            20,
            path=self.test_file,
        )

        updated_stock = change_stock(
            product["product_id"],
            10,
            path=self.test_file,
        )

        self.assertEqual(updated_stock["stock_quantity"], 30)

    def test_07_remove_more_stock_than_available_rejected(self):
        # Reject removing more stock than is currently available.
        product = add_product(
            "Testing Product",
            "12.50",
            20,
            path=self.test_file,
        )

        with self.assertRaises(ValueError):
            change_stock(
                product["product_id"],
                -100000,
                path=self.test_file,
            )

        reloaded = list_products(path=self.test_file)
        self.assertEqual(reloaded[0]["stock_quantity"], 20)

    def test_08_update_non_existing_product_rejected(self):
        # Raise ValueError when updating a non-existing product ID.
        with self.assertRaises(ValueError):
            update_product(
                "P999",
                name="Dummy",
                path=self.test_file,
            )

    def test_09_check_product_availability(self):
        # Return True when sufficient stock exists for requested quantity.
        product = add_product(
            "Testing Product",
            "12.50",
            20,
            path=self.test_file,
        )

        available = check_availability(
            product["product_id"],
            5,
            path=self.test_file,
        )

        self.assertIs(available, True)

    def test_10_close_and_reopen_persistence(self):
        # Verify added product remains saved when reloading from disk.
        product = add_product(
            "Testing Product",
            "12.50",
            20,
            path=self.test_file,
        )

        reloaded_products = list_products(path=self.test_file)
        found = any(p["product_id"] == product["product_id"] for p in reloaded_products)

        self.assertTrue(found)

    def test_11_view_inventory(self):
        # Verify stored product records are returned when listing inventory.
        add_product("Product One", "10.00", 5, path=self.test_file)
        add_product("Product Two", "20.00", 8, path=self.test_file)

        products = list_products(path=self.test_file)

        self.assertEqual(len(products), 2)

    def test_12_performance_load_200_products(self):
        # Verify loading 200 products takes less than 2 seconds.
        for i in range(1, 201):
            add_product(
                f"Performance Test Product {i}",
                "10.00",
                100,
                path=self.test_file,
            )

        start = time.perf_counter()
        products = list_products(path=self.test_file)
        duration = time.perf_counter() - start

        print(f"\n    [Timing] Loaded {len(products)} products in {duration:.4f}s")
        self.assertEqual(len(products), 200)
        self.assertLess(duration, 2.0)

if __name__ == "__main__":
    print("=" * 60)
    print("Increment 1 - Testing & Validation (unittest)")
    print("=" * 60)
    unittest.main(verbosity=2)
