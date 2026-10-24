try:
    # Import the inventory engineering core module provided by Steven
    import inventory as inv
except ImportError:
    inv = None
    print("Warning: inventory.py module was not detected in the current path. Running in Mock Mode.")

def display_inventory_menu():
    # Handles numerical inputs 
    while True:
        # Displaying the inventory control UI dashboard onto the console screen
        print("\n==================================")
        print("    E-Shop Inventory Menu         ")
        print("==================================")
        print("1. View Inventory")
        print("2. Add Product")
        print("3. Update Product Information")
        print("4. Change Stock")
        print("5. Check Product Availability")
        print("6. Return to Main Menu")
        print("==================================")
        
        choice = input("Please enter your selection (1-6): ").strip()
        
        if choice == '1':
            print("\n--- [Action] Listing Product Records ---")
            if inv:
                try:
                    products = inv.list_products()
                    if not products:
                        print("Notification: The active product inventory ledger is currently empty.")
                    else:
                        # Iterate through data structures synchronized from products.json
                        for p in products:
                            print(f"ID: {p['product_id']} | Name: {p['product_name']} | Price: ${p['price']} | Stock: {p['stock_quantity']}")
                except Exception as e:
                    print(f"System Error: Failed to load inventory ledger. {e}")
            else:
                print("[Mock Mode] Fetching and rendering rows from products.json...")

        elif choice == '2':
            print("\n--- [Action] Creating Newly Added Product ---")
            name = input("Enter new product name: ").strip()
            price = input("Enter unit price (e.g., 12.50): ").strip()
            try:
                starting_stock = int(input("Enter baseline initial stock level: "))
                
                if inv:
                    # Capture potential ValueErrors 
                    created_product = inv.add_product(name, price, starting_stock)
                    print(f"Success: Stored record for '{created_product['product_name']}' with allocated ID {created_product['product_id']}.")
                else:
                    print(f"[Mock Mode] Successfully staged mock product record for: {name}")
            except ValueError as e:
                print(f"Input Rejected: {e}")

        elif choice == '3':
            print("\n--- [Action] Updating An Existing Product ---")
            product_id = input("Enter Target Product ID (e.g., P001): ").strip()
            name_input = input("Enter updated name string (Press Enter to retain original): ").strip()
            price_input = input("Enter updated price string (Press Enter to retain original): ").strip()
            
            # Optional arguments
            name = name_input if name_input != "" else None
            price = price_input if price_input != "" else None
            
            if inv:
                try:
                    updated_product = inv.update_product(product_id, name, price)
                    print(f"Success: Record {updated_product['product_id']} updated. Name: {updated_product['product_name']}, Price: ${updated_product['price']}")
                except ValueError as e:
                    print(f"Update Aborted: {e}")
            else:
                print(f"[Mock Mode] Staged update attributes for product token: {product_id}")

        elif choice == '4':
            print("\n--- [Action] Changing Existing Stock Quantity ---")
            product_id = input("Enter Target Product ID (e.g., P001): ").strip()
            print("To add stock, enter a positive number (e.g., 10). To remove, enter a negative number (e.g., -5).")
            try:
                
                stock_change = int(input("Enter stock adjustment value (nonzero integer): "))
                
                if inv:
                    updated_product = inv.change_stock(product_id, stock_change)
                    print(f"Success: Adjusted inventory levels. Current stock for {product_id} is now: {updated_product['stock_quantity']}")
                else:
                    print(f"[Mock Mode] Invoked change trace. Asset {product_id} shifted by {stock_change} units.")
            except ValueError as e:
                print(f"Adjustment Refused: {e}")

        elif choice == '5':
            print("\n--- [Action] Checking Product Availability ---")
            product_id = input("Enter Target Product ID: ").strip()
            try:
                qty = int(input("Enter required checkout quantity threshold: "))
                
                if inv:
                   
                    available = inv.check_availability(product_id, qty)
                    if available:
                        print(f"Evaluation Result: True. Sufficient inventory buffer exists for product {product_id}.")
                    else:
                        print(f"Evaluation Result: False. Insufficient stock units available for request size.")
                else:
                    print(f"[Mock Mode] Evaluated local buffer availability trace for item: {product_id}")
            except ValueError as e:
                print(f"Query Denied: {e}")

        elif choice == '6':
            print("\nExiting sub-menu hierarchy. Returning to main console loop.")
            break
            
        else:
            print("Selection Rejected: Invalid command token. Please select an option bounded between 1 and 6.")

if __name__ == "__main__":
    display_inventory_menu()
