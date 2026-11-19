# =========================================================
# Unit Tests for inventory_menu.py (unittest)
# Prepared by Louis
# Purpose: Verify that the Inventory Menu Module
#          functions correctly using unittest.
# =========================================================

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import inventory as inv_core
import inventory_menu
from storage import save_products


class TestInventoryMenu(unittest.TestCase):
    # Tests for the E-Shop Inventory Menu console workflow.

    def setUp(self):
        # Create a temporary products file and bind inventory_menu.inv to it.
        self.test_file = Path("test_inventory_menu_products.json")
        if self.test_file.exists():
            self.test_file.unlink()

        save_products(
            [
                {
                    "product_id": "P001",
                    "product_name": "Notebook",
                    "price": "25.00",
                    "stock_quantity": 10,
                }
            ],
            path=self.test_file,
        )

        self.orig_list_products = inv_core.list_products
        self.orig_add_product = inv_core.add_product
        self.orig_update_product = inv_core.update_product
        self.orig_change_stock = inv_core.change_stock
        self.orig_check_availability = inv_core.check_availability

        test_path = self.test_file
        inv_core.list_products = lambda path=test_path: self.orig_list_products(path=path)
        inv_core.add_product = lambda name, price, starting_stock, path=test_path: self.orig_add_product(
            name, price, starting_stock, path=path
        )
        inv_core.update_product = lambda product_id, name=None, price=None, path=test_path: self.orig_update_product(
            product_id, name=name, price=price, path=path
        )
        inv_core.change_stock = lambda product_id, change, path=test_path: self.orig_change_stock(
            product_id, change, path=path
        )
        inv_core.check_availability = lambda product_id, quantity, path=test_path: self.orig_check_availability(
            product_id, quantity, path=path
        )

    def tearDown(self):
        # Restore original inventory functions and remove temporary test file.
        inv_core.list_products = self.orig_list_products
        inv_core.add_product = self.orig_add_product
        inv_core.update_product = self.orig_update_product
        inv_core.change_stock = self.orig_change_stock
        inv_core.check_availability = self.orig_check_availability

        if self.test_file.exists():
            self.test_file.unlink()

    def test_view_add_update_stock_availability_and_exit(self):
        # Exercise options 1 through 5 and exit cleanly on option 6.
        inputs = [
            "1",                      # View Inventory
            "2", "Pen", "5.00", "30", # Add Product
            "3", "P001", "Grid Notebook", "28.00",  # Update Product
            "4", "P001", "5",         # Change Stock (+5)
            "5", "P001", "10",        # Check Availability
            "6",                      # Return to Main Menu
        ]
        buf = io.StringIO()
        with (
            patch("inventory_menu.inv", inv_core),
            patch("builtins.input", side_effect=inputs),
            redirect_stdout(buf),
        ):
            inventory_menu.display_inventory_menu()

        output = buf.getvalue()
        self.assertIn("Notebook", output)
        self.assertIn("allocated ID P002", output)
        self.assertIn("Grid Notebook", output)
        self.assertIn("now: 15", output)
        self.assertIn("Evaluation Result: True.", output)
        self.assertIn("Returning to main console loop.", output)

    def test_invalid_choice_and_validation_rejection(self):
        # Reject invalid menu options and surface ValueError messages.
        inputs = [
            "99",                   # Invalid option
            "2", "", "12.50", "10", # Empty name rejected
            "6",                    # Exit
        ]
        buf = io.StringIO()
        with (
            patch("inventory_menu.inv", inv_core),
            patch("builtins.input", side_effect=inputs),
            redirect_stdout(buf),
        ):
            inventory_menu.display_inventory_menu()

        output = buf.getvalue()
        self.assertIn("Selection Rejected:", output)
        self.assertIn("Input Rejected: Product name cannot be empty", output)


if __name__ == "__main__":
    print("=" * 60)
    print("Unit Tests for inventory_menu.py (unittest)")
    print("=" * 60)
    unittest.main(verbosity=2)
