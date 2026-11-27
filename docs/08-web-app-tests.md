# Web Interface Tests — Documentation

Group 65 · COMP 8500SEF Software Engineering · 28 November 2026

The console menus are covered in `07-menu-tests.md`.
This document covers the browser interface in `web_app.py`, which exposes the same modules over HTTP.
Each test starts the server on a test port, sends real requests and checks the JSON it gets back and the data files it leaves behind.

## 1 Web interface

The tests are implemented in `Products/test_web_app.py` with the `unittest` framework, in 5 test methods.
The suite runs against a temporary copy of the data files, which it creates and deletes, and starts a server on a test port for the duration of each test.
It can be run directly as a script or with `python -m unittest test_web_app`.

| # | Test method | Expected result | Result |
|---|---|---|---|
| 1 | `test_01_get_index_html_and_state` | `GET /` returns the page and `GET /api/state` returns the current data as JSON | PASS |
| 2 | `test_02_product_crud_and_stock_adjustment` | Adding a product, updating it and adjusting its stock all succeed through the API | PASS |
| 3 | `test_03_end_to_end_order_and_delivery_lifecycle` | An order is packed, assigned as Courier, started and completed | PASS |
| 4 | `test_04_cancel_order_and_validation_errors` | A Pending order is cancelled, and an invalid request answers with an error instead of changing the data | PASS |
| 5 | `test_05_reset_demo_restores_initial_snapshot` | `POST /api/reset` restores the starting products and orders | PASS |

Overall: 5 of 5 passed. Each test starts its own server and a temporary copy of the data files.
