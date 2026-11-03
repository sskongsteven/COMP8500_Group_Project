# Increment 2 — Documentation

Group 65 · COMP 8500SEF Software Engineering · 3 November 2026

## 1 Order workflow

Increment 2 adds the order area. Orders are read from orders.json; a staff member picks an order ID, and the program either shows the record or moves it to a new status. All rules live in order.py, so the menu cannot bypass them.

    order_menu.py
      1 -> view one order: header, items, total and the full status history
      2 -> mark as Packed
      3 -> update status: 1 Ready for Delivery / 2 Out for Delivery / 3 Delivered
      4 -> cancel: only allowed while the order is Pending
      5 -> return to the main menu

Status machine:

    Pending --> Packed --> Ready for Delivery --> Out for Delivery --> Delivered
       |
       +--> Cancelled            (allowed only from Pending)

| Transition | Allowed from | Rejected with |
|---|---|---|
| to Packed | Pending only | "Rule Violation: Only Pending orders can transition to Packed. Current: ..." |
| to Ready for Delivery | Packed only | "Rule Violation: Only Packed orders can transition to Ready for Delivery. Current: ..." |
| to Out for Delivery | Ready for Delivery only | "Rule Violation: Only Ready for Delivery orders can transition to Out for Delivery. Current: ..." |
| to Delivered | Out for Delivery only | "Rule Violation: Only Out for Delivery orders can transition to Delivered. Current: ..." |
| to Cancelled | Pending only | "Rule Violation: Orders can only be cancelled while Pending. Packing has already structuralized this order." |
| any unknown status | never | "Invalid status identifier token: ..." |
| order ID not in the file | never | "Order ID ... was not found." |

Two behaviours are worth stating because they are easy to miss. First, requesting the status an order already has is a no-op: the record is returned unchanged and no history entry is added. Second, every accepted change appends an entry to status_history with the new status and the time it happened, so the audit trail and the current status can never disagree.

## 2 Test summary

The tests are implemented in Products/test_increment2.py. Each case records its expected result, its actual result and a PASS or FAIL status, and the script prints a summary with the pass count and pass rate. Tests run against a temporary file, test_orders.json, which the script creates and deletes, so the real orders.json is never modified.

| # | Test | Expected result | Result |
|---|---|---|---|
| 1 | View order details | Correct order information displayed | TBC |
| 2 | Mark order as packed | Status changes to Packed | TBC |
| 3 | Update to Ready for Delivery | Status changes successfully | TBC |
| 4 | Update to Out for Delivery | Status changes successfully | TBC |
| 5 | Update to Delivered | Status changes successfully | TBC |
| 6 | Cancel a Pending order | Status changes to Cancelled | TBC |
| 7 | Cancel a Packed order | Rejected | TBC |
| 8 | Non-existing order | Error displayed | TBC |
| 9 | Reopen program | Status persists | TBC |
| 10 | Pending -> Ready for Delivery | Rejected | TBC |
| 11 | Pending -> Out for Delivery | Rejected | TBC |
| 12 | Pending -> Delivered | Rejected | TBC |
| 13 | Packed -> Out for Delivery | Rejected | TBC |
| 14 | Packed -> Delivered | Rejected | TBC |
| 15 | Ready for Delivery -> Delivered | Rejected | TBC |
| 16 | Cancel a Ready for Delivery order | Rejected | TBC |
| 17 | Cancel an Out for Delivery order | Rejected | TBC |
| 18 | Cancel a Delivered order | Rejected | TBC |
| 19 | Status history update verification | New status appended to status_history | TBC |
| 20 | Invalid status value | Rejected | TBC |
| 21 | Empty order file | Zero orders loaded successfully | TBC |
| 22 | Performance test (100 orders) | 100 orders loaded within 2 seconds | TBC |

Overall: __ of 22 passed.

The Result column is filled in from the actual test run; TBC marks cases that have not been recorded yet.

## 3 Limitations

| # | Limitation | Effect |
|---|---|---|
| 1 | Orders cannot be created in the application | This increment works from the sample order file; manual entry is not implemented |
| 2 | There is no way to move an order back to an earlier status | A transition made in error can only be corrected by editing the data file |
| 3 | Delivery details are null | The delivery object is added when delivery assignment is built in Increment 3 |
| 4 | No roles or authorisation | Anyone who can run the console can change any order status |
