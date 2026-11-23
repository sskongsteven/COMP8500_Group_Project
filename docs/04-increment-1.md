# Increment 1 — Documentation

Group 65 · COMP 8500SEF Software Engineering · 23 November 2026

## 1 Inventory workflow

The program starts at `main_menu.py`, which offers three areas. This document covers the inventory
area (option 1); options 2 and 3 open the order and delivery menus, which are documented in
`05-increment-2.md` and `06-increment-3.md`. Inside the inventory submenu, all five operations follow
the same path: validate the input, load the data file, change the list in memory, save the file,
report the result. Only "view inventory" and "check availability" read without writing.

    main_menu.py
      1 -> inventory_menu.py -> the five operations below
      2 -> order_menu.py
      3 -> delivery_menu.py
      0 -> exit

    Inside inventory_menu.py:
      print the menu (1-6), read the choice
        |
        +-- 1 View        load_products  ->  print each record        (no write)
        +-- 2 Add         validate name / price / stock
        |                 load -> allocate P### -> append -> save
        +-- 3 Update      validate name and/or price
        |                 load -> find -> change -> save
        +-- 4 Change stock validate nonzero integer
        |                 load -> find -> apply change
        |                 validate the RESULTING quantity -> save
        +-- 5 Availability validate quantity > 0
        |                 load -> find -> compare -> print True/False (no write)
        +-- 6 Return      leave the loop
        |
      a ValueError is caught, printed with a prefix, and the menu is shown again

| Option | Action | Validation applied | Writes products.json |
|---|---|---|---|
| 1 | View inventory | none | No |
| 2 | Add product | name non-empty; price two decimals, not negative; stock whole number, not negative | Yes |
| 3 | Update product | at least one of name and price; same rules as option 2 | Yes |
| 4 | Change stock | change is a non-zero integer; the resulting stock must not be negative | Yes, unless the result would be negative |
| 5 | Check availability | quantity greater than zero | No |
| 6 | Return | none | No |

Two details follow from the code. The stock change validates the quantity after the adjustment, so removing 20 units from a stock of 5 is refused before anything is written. Every save goes through a temporary file that is synced to disk and then renamed over products.json, so a crash during a write cannot leave a half-written file.

## 2 Test summary

The tests are implemented in `Products/test_increment1.py` with the `unittest` framework, in 12 test
methods. The suite runs against a temporary file, `test_products.json`, which it creates and deletes,
so the real `products.json` is never modified. It can be run directly as a script or with
`python -m unittest test_increment1`.

| # | Test method | Expected result | Result |
|---|---|---|---|
| 1 | Add a valid product | Product receives a unique ID and appears in inventory | PASS |
| 2 | Add a product with an empty name | Rejected, file unchanged | PASS |
| 3 | Negative price | Rejected, file unchanged | PASS |
| 4 | Negative starting stock | Rejected, file unchanged | PASS |
| 5 | Update product information | Changes reflected in inventory | PASS |
| 6 | Add stock | Quantity in inventory increases | PASS |
| 7 | Remove more stock than available | Rejected, quantity unchanged | PASS |
| 8 | Update a non-existing product | Show error, no change | PASS |
| 9 | Check product availability | True when sufficient stock exists | PASS |
| 10 | Close and reopen program | Products are correctly saved | PASS |
| 11 | View inventory | Inventory records are displayed | PASS |
| 12 | Performance test (inventory with 200 products) | 200 products loaded within 2 seconds | PASS |

Overall: 12 of 12 passed. The performance case loaded 200 products in 0.0002 seconds, well inside the two-second target.

## 3 Limitations

This section describes Increment 1 as delivered on 26 October.

| # | Limitation | Effect |
|---|---|---|
| 1 | Product identifiers are the highest existing number plus one | If deletion is added later, deleting the highest product would allow its identifier to be reused |
| 2 | A non-numeric entry shows the Python error message | Typing text where a number is expected prints "invalid literal for int() with base 10" instead of a clear hint |
