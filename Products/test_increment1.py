# =========================================================
# Increment 1 - Testing & Validation
# Prepared by Louis
# Purpose: Verify that the Product & Inventory Module 
#          functions correctly.
# =========================================================

# Import standard Python libraries.
import os
import time

# Import inventory management functions.
from inventory import (
    add_product,
    update_product,
    change_stock,
    check_availability,
    list_products
)

# Name of temporary file used for testing.
# This prevents changes to the actual products.json.
TEST_FILE = "test_products.json"

# ---------------------------------------------------------
# Create clean test file
# ---------------------------------------------------------

# Remove any previous test file before testing.
if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)

# Store all test results for summary reporting.
results = []

# Display the test result and save it to the summary list.
def record(test_case, expected, actual, passed):
    status = "PASS" if passed else "FAIL"
    results.append(
        (
            test_case,
            expected,
            actual,
            status
        )
    )
    print("\n" + "-" * 60)
    print(f"Test Case      : {test_case}")
    print(f"Expected Result: {expected}")
    print(f"Actual Result  : {actual}")
    print(f"Result         : {status}")
print("=" * 60)
print("Increment 1 - Testing & Validation")
print("=" * 60)

# ---------------------------------------------------------
# Test 1 - Add a valid product
# ---------------------------------------------------------

try:
    # Create a valid test product.
    product = add_product(
        "Testing Product",
        "12.50",
        20,
        path=TEST_FILE
    )
    products = list_products(path=TEST_FILE)

    # Check whether the product was added successfully.
    found = any(
        p["product_id"] == product["product_id"]
        for p in products
    )

    # Record PASS/FAIL result.
    record(
        "Add a valid product",
        "Product receives a unique ID and appears in inventory",
        f"Created Product ID {product['product_id']}",
        found
    )

# Catch any unexpected error that occurs during this test.
# Store the error message in variable 'e'.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Add a valid product",
        "Product receives a unique ID and appears in inventory",
        str(e),        # Convert the error message to text.
        False          # Test failed.  
    )

# ---------------------------------------------------------
# Test 2 - Add a product with an empty name
# ---------------------------------------------------------

try:
    # Attempt to create a product with an empty name.
    add_product(
        "",
        "12.50",
        20,
        path=TEST_FILE
    )

    # Record True/False result.
    record(
        "Add a product with an empty name",
        "Rejected, file unchanged",
        "Empty product name accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result
    record(
        "Add a product with an empty name",
        "Rejected, file unchanged",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 3 - Enter a negative or invalid price
# ---------------------------------------------------------

try:
    # Attempt to create a product with a negative price.
    add_product(
        "Negative Price Product",
        "-5.00",
        20,
        path=TEST_FILE
    )

    # Record True/False result.
    record(
        "Negative price",
        "Rejected, file unchanged",
        "Negative price accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result
    record(
        "Negative price",
        "Rejected, file unchanged",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 4 - Enter negative starting stock
# ---------------------------------------------------------

try:
    # Attempt to create a product with a negative starting stock.
    add_product(
        "Negative Stock Product",
        "12.50",
        -10,
        path=TEST_FILE
    )

    # Record True/False result.
    record(
        "Negative starting stock",
        "Rejected, file unchanged",
        "Negative stock accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Negative starting stock",
        "Rejected, file unchanged",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 5 - Update product name or price
# ---------------------------------------------------------

try:
    # Update the name and price of the test product.
    updated = update_product(
        product["product_id"],
        name="Updated Testing Product",
        price="15.00",
        path=TEST_FILE
    )

    # Check whether the update was successful.
    passed = (
        updated["product_name"] == "Updated Testing Product"
        and updated["price"] == "15.00"
    )

    # Record PASS/FAIL result.
    record(
        "Update product information",
        "Changes reflected in inventory",
        f"Name={updated['product_name']}, Price={updated['price']}",
        passed
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Update product information",
        "Changes reflected in inventory",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 6 - Add stock
# ---------------------------------------------------------

try:
    # Add stock to the test product.
    before = updated["stock_quantity"]
    updated_stock = change_stock(
        product["product_id"],
        10,
        path=TEST_FILE
    )
    actual_stock = updated_stock["stock_quantity"]

    # Check whether the stock quantity increased successfully.
    passed = (
        actual_stock == before + 10
    )

    # Record PASS/FAIL result.
    record(
        "Add stock",
        "Quantity in inventory increases",
        f"Stock changed from {before} to {actual_stock}",
        passed
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Add stock",
        "Quantity in inventory increases",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 7 - Remove more stock than available
# ---------------------------------------------------------

try:
    # Attempt to remove more stock than is available.
    change_stock(
        product["product_id"],
        -100000,
        path=TEST_FILE
    )
    
    # Record True/False result.
    record(
        "Remove more stock than available",
        "Rejected, quantity unchanged",
        "Operation accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Remove more stock than available",
        "Rejected, quantity unchanged",
        "Validation error raised",
        True
    )

# ---------------------------------------------------------
# Test 8 - Select a non-existing product
# ---------------------------------------------------------

try:
    # Update the non-existing product.
    update_product(
        "P999",
        name="Dummy",
        path=TEST_FILE
    )

    # Record True/False result.
    record(
        "Select a non-existing product",
        "Show error, no change",
        "Non-existing product accepted",
        False
    )

# Catch any expected error.
except ValueError:

    # Record the error as the actual result.
    record(
        "Select a non-existing product",
        "Show error, no change",
        "Product not found error raised",
        True
    )

# ---------------------------------------------------------
# Test 9 - Check product availability
# ---------------------------------------------------------

try:
    # Check the availability of the test product.
    available = check_availability(
        product["product_id"],
        5,
        path=TEST_FILE
    )

    # Record the availability check result.
    record(
        "Check product availability",
        "True when sufficient stock exists",
        f"Availability = {available}",
        available
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Check product availability",
        "True when sufficient stock exists",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 10 - Close and reopen program
# ---------------------------------------------------------

try:
    # Reload product records from the test file.
    reloaded_products = list_products(
        path=TEST_FILE
    )

    # Check whether the product is still present after reloading.
    found = any(
        p["product_id"] == product["product_id"]
        for p in reloaded_products
    )

    # Record PASS/FAIL result.
    record(
        "Close and reopen program",
        "Products are correctly saved",
        "Product found after reload",
        found
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Close and reopen program",
        "Products are correctly saved",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 11 - View Inventory
# ---------------------------------------------------------

try:
    # Retrieve all product records from the test file.
    products = list_products(path=TEST_FILE)

    # Record list result.
    record(
        "View inventory",
        "Inventory records are displayed",
        f"{len(products)} products loaded",
        len(products) > 0
    )

# Catch any unexpected error.
except Exception as e:

    record(
        "View inventory",
        "Inventory records are displayed",
        str(e),
        False
    )

# ---------------------------------------------------------
# Test 12 - Performance test
# ---------------------------------------------------------

try:
    # Create additional products until the
    # test inventory contains 200 products.
    current_products = list_products(
        path=TEST_FILE
    )
    current_count = len(current_products)
    for i in range(current_count + 1, 201):
        add_product(
            f"Performance Test Product {i}",
            "10.00",
            100,
            path=TEST_FILE
        )

    # Measure inventory retrieval performance.
    start = time.time()
    products = list_products(
        path=TEST_FILE
    )
    end = time.time()
    duration = end - start

    # Confirm that 200 products exist.
    actual_count = len(products)

    # Record performance result.
    record(
        "Performance test (inventory with 200 products)",
        "200 products loaded within 2 seconds",
        f"{actual_count} products loaded in {duration:.4f} seconds",
        actual_count == 200 and duration < 2
    )

# Catch any unexpected error.
except Exception as e:

    # Record the error as the actual result.
    record(
        "Performance test (inventory with 200 products)",
        "200 products loaded within 2 seconds",
        str(e),
        False
    )

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
pass_count = 0
for item in results:
    test_case, expected, actual, status = item
    if status == "PASS":
        pass_count += 1

    # Display the PASS/FAIL status for all test cases.
    print(
        f"{status:5} | {test_case}"
    )

# Calculate the total number of passed tests.
print(
    f"\nPassed: {pass_count}/{len(results)}"
)

# ---------------------------------------------------------
# Remove test file
# ---------------------------------------------------------

# Remove the temporary test file to ensure
# future test runs start with a clean environment.
if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)
print("\nTest file removed: test_products.json")
