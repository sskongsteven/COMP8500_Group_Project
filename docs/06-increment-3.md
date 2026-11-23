# Increment 3 — Documentation

Group 65 · COMP 8500SEF Software Engineering · 23 November 2026

## 1 Delivery workflow

Increment 3 adds the delivery and tracking area. The main menu routes option 3 to `delivery_menu.py`,
which reads and writes the same `orders.json` as the order module through `storage.py`.

    main_menu.py
      3 -> delivery_menu.py -> the five operations and a return option below

    Inside delivery_menu.py:
      1 -> view one order's delivery: method, driver and delivery status
      2 -> assign a delivery: method first, then a driver when the method is Courier
      3 -> start the delivery
      4 -> complete the delivery
      5 -> view order tracking: order status, delivery status and the full history
      6 -> return to the main menu

Options 1 to 5 first print the orders as a numbered list; entering 0 cancels and returns to the
delivery menu.

A delivery moves through four states:

    Unassigned --> Assigned --> In Transit --> Delivered

The order module owns the first two order states, Pending to Packed and Pending to Cancelled. The
delivery module owns the rest, and each delivery step advances the order by one state.

| Step | Delivery status | Order status | Rejected with |
|---|---|---|---|
| Assign | Unassigned -> Assigned | Packed -> Ready for Delivery | "Only Packed orders can be assigned." |
| Start | Assigned -> In Transit | Ready for Delivery -> Out for Delivery | "Delivery must be Assigned." |
| Complete | In Transit -> Delivered | Out for Delivery -> Delivered | "Delivery must be In Transit." |

Assigning also needs a valid method and, for Courier, a valid driver:

| Input | Rule | Rejected with |
|---|---|---|
| Method | 1 for Courier, 2 for Self Pickup | "Invalid delivery method." |
| Driver (Courier only) | must exist in the driver table D001-D003 | "Invalid driver." |
| Order ID | must exist in `orders.json` | "Order not found." |

Self Pickup records no driver: both `driver_id` and `driver_name` are set to `null`, so the delivery
object is still present and still tracked. Every step is appended to `status_history` with a
timestamp through the shared helper in `common.py`, so the tracking view prints the whole sequence. Saving goes through `storage.py`, which writes a temporary file, syncs it and replaces `orders.json` in one step.

The menu catches each raised error and prints it with a stage-specific prefix, so the operator can
tell which step failed: "Assignment Rejected", "Transition Rejected", "Completion Rejected" or
"Query Denied", followed by the message from the table above.

## 2 Test summary

The tests are implemented in `Products/test_increment3.py` with the `unittest` framework, in 14 test
methods. They run against temporary copies of `orders.json` and `products.json`, so the real data
files are never modified.

| # | Test method | Expected result |
|---|---|---|
| 1 | `test_01_view_delivery_details` | Method, driver and delivery status are printed |
| 2 | `test_02_view_order_tracking` | Order status, delivery status and history are printed |
| 3 | `test_03_assign_courier_delivery` | Delivery becomes Assigned; order becomes Ready for Delivery |
| 4 | `test_04_assign_self_pickup_delivery` | Driver fields stay null; order becomes Ready for Delivery |
| 5 | `test_05_reject_assign_non_packed_order` | Rejected: "Only Packed orders can be assigned." |
| 6 | `test_06_reject_invalid_driver_selection` | Rejected: "Invalid driver." |
| 7 | `test_07_start_delivery_after_assignment` | Delivery becomes In Transit; order becomes Out for Delivery |
| 8 | `test_08_reject_start_delivery_before_assignment` | Rejected: "Delivery must be Assigned." |
| 9 | `test_09_complete_delivery_successfully` | Delivery and order both become Delivered |
| 10 | `test_10_reject_complete_delivery_before_in_transit` | Rejected: "Delivery must be In Transit." |
| 11 | `test_11_reopen_program_persistence` | Delivery state and history survive a reload |
| 12 | `test_12_reject_invalid_order_id` | Rejected: "Order not found." |
| 13 | `test_13_delivery_status_history_verification` | One entry per step, with timestamps |
| 14 | `test_14_performance_load_100_delivery_orders` | 100 orders loaded inside the two-second target |

## 3 Limitations

| # | Limitation | Effect |
|---|---|---|
| 1 | A delivery is assigned once | The method and driver are set at assignment |
| 2 | Drivers are a fixed list | The module recognises D001, D002 and D003; adding a driver requires a code change |
