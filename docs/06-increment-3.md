# Increment 3 — Documentation

Group 65 · COMP 8500SEF Software Engineering · 16 November 2026

## 1 Delivery workflow

Increment 3 adds the delivery and tracking area. The main menu now routes option 3 to
`delivery_menu.py`, which reads and writes the same `orders.json` as the order module: every order
already carries a `delivery` object.

    main_menu.py
      3 -> delivery_menu.py -> the five operations below

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

The delivery status and the order status move together. Each delivery step advances the order by one state.

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

Saving is atomic: the module writes to a temporary file, flushes and syncs it, then replaces
`orders.json`, so a crash during a write cannot leave a half-written file.

The menu catches each raised error and prints it with a stage-specific prefix, so the operator can
tell which step failed: "Assignment Rejected", "Transition Rejected", "Completion Rejected" or
"Query Denied", followed by the message from the table above.

## 2 Test summary

Increment 3 does not have an automated test script yet. The cases below describe the expected
behaviour of the delivery module.

| # | Test | Expected result |
|---|---|---|
| 1 | Assign Courier to a Packed order | Delivery becomes Assigned; order becomes Ready for Delivery |
| 2 | Assign to an order that is still Pending | Rejected: "Only Packed orders can be assigned." |
| 3 | Assign with an unknown driver ID | Rejected: "Invalid driver." |
| 4 | Assign with a method other than 1 or 2 | Rejected: "Invalid delivery method." |
| 5 | Assign with Self Pickup | Driver fields stay null; order becomes Ready for Delivery |
| 6 | Start a delivery that has not been assigned | Rejected: "Delivery must be Assigned." |
| 7 | Start an assigned delivery | Delivery becomes In Transit; order becomes Out for Delivery |
| 8 | Complete a delivery that is not in transit | Rejected: "Delivery must be In Transit." |
| 9 | Complete an in-transit delivery | Delivery and order both become Delivered |
| 10 | Assign the same order twice | Rejected: "Only Packed orders can be assigned." |
| 11 | View tracking after two transitions | Full history printed in order |
| 12 | Close and reopen the program | Delivery state and history persist |
| 13 | Any operation on an unknown order ID | Rejected: "Order not found." |

## 3 Limitations

| # | Limitation | Effect |
|---|---|---|
| 1 | A delivery is assigned once | The method and driver are set at assignment; changing them afterwards is not supported in this release, so a wrong entry is corrected by editing `orders.json` |
| 2 | Drivers are a fixed list | The module recognises D001, D002 and D003; adding a driver requires a code change rather than a data change |
