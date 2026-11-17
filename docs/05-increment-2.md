# Increment 2 — Documentation

Group 65 · COMP 8500SEF Software Engineering · 14 November 2026

## 1 Order workflow

Increment 2 adds the order area. Orders are read from orders.json; a staff member picks an order ID, and the program either shows the record or moves it to a new status. All rules live in order.py. Packing is the one operation that changes a second file: it deducts stock from `products.json` before the order becomes Packed.

    order_menu.py
      1 -> view one order: header, items, total and the full status history
      2 -> mark as Packed: checks the stock, deducts it, then saves both files
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

### Packing deducts stock

`pack_order(order_id)` performs this step. It checks that the order is Pending and has items, combines repeated lines for the same product, and confirms that each product has enough stock. If any check fails, nothing is written and the error names the shortfall, for example "Insufficient stock for P001: required 3, available 1.". If every check passes, the quantities are subtracted, both files are saved, the order becomes Packed and the change is appended to `status_history`.

An order can only be cancelled while Pending, so a cancelled order has not taken any stock.

Implemented in Increment 2, 12 November 2026.

## 2 Test summary


The tests are implemented in Products/test_increment2.py. Each case records its expected result, its actual result and a PASS or FAIL status, and the script prints a summary with the pass count and pass rate. Tests run against two temporary files, test_products.json and test_orders.json, which the script creates and deletes, so the real products.json and orders.json are never modified.

| # | Test | Expected result | Result |
|---|---|---|---|
| 1 | List all orders | All orders return successfully | PASS |
| 2 | View order details | Correct order information displayed | PASS |
| 3 | Mark order as packed | Status changes to Packed | PASS |
| 4 | Update to Ready for Delivery | Status changes successfully | PASS |
| 5 | Update to Out for Delivery | Status changes successfully | PASS |
| 6 | Update to Delivered | Status changes successfully | PASS |
| 7 | Cancel a Pending order | Status changes to Cancelled | PASS |
| 8 | Cancel a Packed order | Rejected | PASS |
| 9 | Non-existing order | Error displayed | PASS |
| 10 | Reopen program | Status persists | PASS |
| 11 | Pending -> Ready for Delivery | Rejected | PASS |
| 12 | Pending -> Out for Delivery | Rejected | PASS |
| 13 | Pending -> Delivered | Rejected | PASS |
| 14 | Packed -> Out for Delivery | Rejected | PASS |
| 15 | Packed -> Delivered | Rejected | PASS |
| 16 | Ready for Delivery -> Delivered | Rejected | PASS |
| 17 | Cancel a Ready for Delivery order | Rejected | PASS |
| 18 | Cancel an Out for Delivery order | Rejected | PASS |
| 19 | Cancel a Delivered order | Rejected | PASS |
| 20 | Status history update verification | New status appended to status_history | PASS |
| 21 | Invalid status value | Rejected | PASS |
| 22 | Empty order file | Zero orders loaded successfully | PASS |
| 23 | Performance test (100 orders) | 100 orders loaded within 2 seconds | PASS |
| 24 | Pack order and deduct stock | Stock quantity reduced from 10 to 8 | PASS |
| 25 | Pack order with insufficient stock | Validation error raised | PASS |
| 26 | Pack same order twice | Validation error raised | PASS |

Overall: 26 of 26 passed, a pass rate of 100%.

## 3 Limitations

| # | Limitation | Effect |
|---|---|---|
| 1 | Orders cannot be created in the application | This increment works from the sample order file; manual entry is not implemented |
| 2 | There is no way to move an order back to an earlier status | A transition made in error can only be corrected by editing the data file |
| 3 | Delivery details are null | The delivery object is added when delivery assignment is built in Increment 3 |
| 4 | No roles or authorisation | Anyone who can run the console can change any order status |
