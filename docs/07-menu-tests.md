# Menu Tests — Documentation

Group 65 · COMP 8500SEF Software Engineering · 28 November 2026

The three increment suites test the rules in `inventory.py`, `order.py` and `delivery.py`. The menu
suites test what sits above them: each test types a sequence of menu choices, then checks what the menu
printed and whether the right file was changed.

## 1 Inventory menu

The tests are implemented in `Products/test_inventory_menu.py` with the `unittest` framework, in 2 test methods. The suite drives the menu with scripted input and runs against a temporary copy of the data files, which it creates and deletes. It can be run directly as a script or with `python -m unittest test_inventory_menu`.

| # | Test method | Expected result | Result |
|---|---|---|---|
| 1 | `test_view_add_update_stock_availability_and_exit` | Each of the six options runs once and option 6 leaves the loop | PASS |
| 2 | `test_invalid_choice_and_validation_rejection` | An invalid choice and invalid field values are rejected with a message, and the menu continues | PASS |

Overall: 2 of 2 passed.

## 2 Order menu

The tests are implemented in `Products/test_order_menu.py` with the `unittest` framework, in 3 test methods. The suite drives the menu with scripted input and runs against a temporary copy of the data files, which it creates and deletes. It can be run directly as a script or with `python -m unittest test_order_menu`.

| # | Test method | Expected result | Result |
|---|---|---|---|
| 1 | `test_view_order_details_and_back_navigation` | Viewing an order prints its details; entering 0 returns to the menu | PASS |
| 2 | `test_pack_order_and_reject_cancelling_packed_order` | Packing succeeds, and cancelling the packed order is refused | PASS |
| 3 | `test_select_order_from_list_rollback_and_invalid_inputs` | An invalid row number is rejected and the list is shown again | PASS |

Overall: 3 of 3 passed.

## 3 Delivery menu

The tests are implemented in `Products/test_delivery_menu.py` with the `unittest` framework, in 4 test methods. The suite drives the menu with scripted input and runs against a temporary copy of the data files, which it creates and deletes. It can be run directly as a script or with `python -m unittest test_delivery_menu`.

| # | Test method | Expected result | Result |
|---|---|---|---|
| 1 | `test_01_view_delivery_details_and_back_navigation` | The delivery details are printed; 0 returns to the menu | PASS |
| 2 | `test_02_full_delivery_workflow_and_tracking` | Assign, start and complete all succeed, and tracking shows every step | PASS |
| 3 | `test_03_reject_assigning_pending_order` | Assigning a Pending order is refused | PASS |
| 4 | `test_04_select_order_from_list_rollback_and_invalid_inputs` | An invalid row number is rejected and the list is shown again | PASS |

Overall: 4 of 4 passed.

## 4 Main menu

The tests are implemented in `Products/test_main_menu.py` with the `unittest` framework, in 2 test methods. The suite drives the menu with scripted input; it only checks routing between menus and does not write the data files. It can be run directly as a script or with `python -m unittest test_main_menu`.

| # | Test method | Expected result | Result |
|---|---|---|---|
| 1 | `test_route_to_all_submenus_and_exit` | Each option opens the matching submenu, and 0 exits | PASS |
| 2 | `test_invalid_selection_then_exit` | An unrecognised choice prints a message and the menu is shown again | PASS |

Overall: 2 of 2 passed.

In total, the four suites run 11 tests and all 11 passed.
