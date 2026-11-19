# =========================================================
# Unit Tests for main_menu.py (unittest)
# Prepared by Louis
# Purpose: Verify that the Main Menu Module
#          functions correctly using unittest.
# =========================================================

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import main_menu


class TestMainMenu(unittest.TestCase):
    # Tests for the top-level menu routing and exit behavior.

    def test_route_to_all_submenus_and_exit(self):
        # Route selections 1, 2, and 3 to sub-menus, then exit on 0.
        buf = io.StringIO()
        with (
            patch("main_menu.display_inventory_menu") as mock_inv_menu,
            patch("main_menu.display_order_menu") as mock_ord_menu,
            patch("main_menu.display_delivery_menu") as mock_del_menu,
            patch("builtins.input", side_effect=["1", "2", "3", "0"]),
            redirect_stdout(buf),
        ):
            main_menu.display_main_menu()

        mock_inv_menu.assert_called_once()
        mock_ord_menu.assert_called_once()
        mock_del_menu.assert_called_once()
        self.assertIn("Thank you for using the system.", buf.getvalue())

    def test_invalid_selection_then_exit(self):
        # Display an invalid option message before exiting on 0.
        buf = io.StringIO()
        with (
            patch("main_menu.display_inventory_menu") as mock_inv_menu,
            patch("main_menu.display_order_menu") as mock_ord_menu,
            patch("main_menu.display_delivery_menu") as mock_del_menu,
            patch("builtins.input", side_effect=["9", "abc", "0"]),
            redirect_stdout(buf),
        ):
            main_menu.display_main_menu()

        mock_inv_menu.assert_not_called()
        mock_ord_menu.assert_not_called()
        mock_del_menu.assert_not_called()
        self.assertIn("Invalid option.", buf.getvalue())


if __name__ == "__main__":
    print("=" * 60)
    print("Unit Tests for main_menu.py (unittest)")
    print("=" * 60)
    unittest.main(verbosity=2)
