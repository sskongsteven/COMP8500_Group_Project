# Increment 2 — Documentation

Group 65 · COMP 8500SEF Software Engineering · 28 November 2026

## 1 Order workflow

Increment 2 adds the order area. Orders are read from `orders.json` through `storage.py`; a staff
member picks an order ID, and the program either shows the record or changes its state.

    order_menu.py
      1 -> view one order: header, items, total and the full status history
      2 -> mark as Packed (checks stock, deducts it, then saves both files)
      3 -> cancel a Pending order
      4 -> return to the main menu

The order module owns two changes only: Pending to Packed and Pending to Cancelled. The three later
states belong to the delivery area, which moves the order on as the delivery progresses:

    Pending --> Packed --> Ready for Delivery --> Out for Delivery --> Delivered
       |
       +--> Cancelled            (allowed only from Pending)

| Operation | Precondition | Effect | Rejected with |
|---|---|---|---|
| Pack | status is Pending | stock deducted, status becomes Packed | "Only Pending orders can be packed. Current: ..." |
| Pack | order has items | items are processed; an empty order is refused | "Cannot pack an order with no items." |
| Pack | every quantity is above zero | quantities are combined per product before the stock check | "Order item quantity must be greater than zero." |
| Pack | stock covers every item | nothing is written if one item fails | "Insufficient stock for P001: required 3, available 1." |
| Cancel | status is Pending | status becomes Cancelled, stock untouched | "Only Pending orders can be cancelled." |
| Any | the order ID exists | — | pack and cancel: "Order ID O001 was not found."; view: "Order ID O001 was not found in the records." |

Two details follow from the code. Packing validates every item before it writes anything, so a failure
leaves both files unchanged. And cancelling is only possible while the order is Pending, which is why
no stock has to be returned.

### Packing deducts stock

`pack_order(order_id)` performs this step. It checks that the order is Pending and has items, combines
repeated lines for the same product, and confirms that each product has enough stock. If every check
passes, the quantities are subtracted, both files are saved, the order becomes Packed and the change
is appended to `status_history`.

## 2 Test summary

The tests are implemented in `Products/test_increment2.py` with the `unittest` framework, in 19 test
methods. The suite runs against two temporary files, `test_products_unittest.json` and
`test_orders_unittest.json`, which it creates and deletes, so the real `products.json` and `orders.json`
are never modified. It can be run directly as a script or with `python -m unittest test_increment2`.

| # | Test method | Expected result | Result |
|---|---|---|---|
| 1 | `test_01_list_all_orders` | All orders in the file are listed | PASS |
| 2 | `test_02_view_order_details` | The record is returned with items, total and history | PASS |
| 3 | `test_03_mark_order_as_packed` | Status becomes Packed | PASS |
| 4 | `test_04_cancel_pending_order` | Status becomes Cancelled | PASS |
| 5 | `test_05_cancel_packed_order_rejected` | Rejected | PASS |
| 6 | `test_06_non_existing_order_rejected` | "Order ID ... was not found." | PASS |
| 7 | `test_07_reopen_program_persistence` | The change survives a reload | PASS |
| 8 | `test_08_cannot_pack_ready_for_delivery_order` | Rejected | PASS |
| 9 | `test_09_cannot_pack_out_for_delivery_order` | Rejected | PASS |
| 10 | `test_10_cannot_pack_delivered_order` | Rejected | PASS |
| 11 | `test_11_cannot_cancel_ready_for_delivery_order` | Rejected | PASS |
| 12 | `test_12_cannot_cancel_out_for_delivery_order` | Rejected | PASS |
| 13 | `test_13_cannot_cancel_delivered_order` | Rejected | PASS |
| 14 | `test_14_status_history_updated_on_pack` | One entry appended with a timestamp | PASS |
| 15 | `test_15_empty_order_file` | Zero orders loaded | PASS |
| 16 | `test_16_performance_load_100_orders` | 100 orders loaded within 2 seconds | PASS |
| 17 | `test_17_pack_order_deducts_stock` | Stock reduced by the ordered quantities | PASS |
| 18 | `test_18_pack_order_insufficient_stock_rejected` | Rejected, both files unchanged | PASS |
| 19 | `test_19_pack_same_order_twice_rejected` | Rejected, stock deducted once only | PASS |

Overall: 19 of 19 passed. The performance case loaded 100 orders in 0.0008 seconds.

## 3 Limitations

| # | Limitation | Effect |
|---|---|---|
| 1 | An order is created outside the application | This increment works from the sample order file; manual entry is not supported |
