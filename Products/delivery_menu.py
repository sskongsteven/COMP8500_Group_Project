try:
    # Import the delivery functions from delivery.py
    import delivery as del_core
except ImportError:
    del_core = None
    print("Warning: delivery.py module was not detected. Running in Mock Mode.")

def select_order_from_list():
    # Helper function to render existing records as a numbered console list.
    # Added 'Option 0' to allow navigation rollback.
    if not del_core:
        print("[Mock Mode] Staged order collection placeholder.")
        return None
        
    orders = del_core.load_orders()
    if not orders:
        print("Notification: There are currently no active orders stored in the JSON file.")
        return None
        
    print("\n--- Available Orders List ---")
    # Loop through the rows and append a numbered visual index (1, 2, 3...).
    for idx, order in enumerate(orders, 1):
        print(f"[{idx}] Order ID: {order['order_id']} | Customer: {order['customer_name']} | Status: {order['status']} | Delivery Status: {order['delivery']['delivery_status']}")
    print("[0] Return to Delivery Menu (Cancel and Go Back)")
    print("------------------------------")
    
    while True:
        try:
            selection_input = input(f"Select an order row (1-{len(orders)}) or enter 0 to go back: ").strip()
            if selection_input == '0':
                print("Action Cancelled: Returning to previous menu window.")
                return "BACK" # Return a special token signaling an intentional go-back choice
                
            selection = int(selection_input)
            if 1 <= selection <= len(orders):
                return orders[selection - 1]["order_id"]
            else:
                print(f"Selection Rejected: Number must be bounded between 0 and {len(orders)}.")
        except ValueError:
            print("Selection Rejected: Operational inputs must be valid numerical integers.")

def display_delivery_menu():
    # Renders the primary text-based delivery and tracking control sub-menu.
    while True:
        print("\n==================================")
        print("    E-Shop Delivery & Tracking    ")
        print("==================================")
        print("1. View Delivery Details")
        print("2. Assign Delivery")
        print("3. Start Delivery")
        print("4. Complete Delivery")
        print("5. View Order Tracking")
        print("6. Return to Main Menu")
        print("==================================")

        choice = input("Please enter your selection (1-6): ").strip()

        if choice == "1":
            while True:
                print("\n--- [Action] View Delivery Details ---")
                selected_id = select_order_from_list()
                
                if selected_id == "BACK":
                    break # Break the sub-loop and return to the delivery menu
                    
                if selected_id and del_core:
                    try:
                        del_core.view_delivery(selected_id)
                    except ValueError as e:
                        print(f"Query Denied: {e}")
                elif not del_core:
                    print(f"[Mock Mode] Viewed delivery details for order {selected_id}")

                # Ask users if they want to view another delivery before returning to the menu.
                another = input("\nDo you want to view another delivery? (y/n): ").strip().lower()
                if another != 'y' and another != 'yes':
                    break

        elif choice == "2":
            print("\n--- [Action] Assign Delivery ---")
            selected_id = select_order_from_list()
            if selected_id == "BACK":
                continue
            if selected_id and del_core:
                try:
                    del_core.assign_delivery(selected_id)
                except ValueError as e:
                    print(f"Assignment Rejected: {e}")
            elif not del_core:
                print(f"[Mock Mode] Assigned delivery for order {selected_id}")

        elif choice == "3":
            print("\n--- [Action] Start Delivery ---")
            selected_id = select_order_from_list()
            if selected_id == "BACK":
                continue
            if selected_id and del_core:
                try:
                    del_core.start_delivery(selected_id)
                except ValueError as e:
                    print(f"Transition Rejected: {e}")
            elif not del_core:
                print(f"[Mock Mode] Started delivery for order {selected_id}")

        elif choice == "4":
            print("\n--- [Action] Complete Delivery ---")
            selected_id = select_order_from_list()
            if selected_id == "BACK":
                continue
            if selected_id and del_core:
                try:
                    del_core.complete_delivery(selected_id)
                except ValueError as e:
                    print(f"Completion Rejected: {e}")
            elif not del_core:
                print(f"[Mock Mode] Completed delivery for order {selected_id}")

        elif choice == "5":
            print("\n--- [Action] View Order Tracking ---")
            selected_id = select_order_from_list()
            if selected_id == "BACK":
                continue
            if selected_id and del_core:
                try:
                    del_core.view_tracking(selected_id)
                except ValueError as e:
                    print(f"Query Denied: {e}")
            elif not del_core:
                print(f"[Mock Mode] Viewed order tracking for order {selected_id}")

        elif choice == "6":
            print("\nExiting sub-menu hierarchy. Returning to main console loop.")
            break

        else:
            print("Selection Rejected: Invalid command token. Please select an option bounded between 1 and 6.")

if __name__ == "__main__":
    display_delivery_menu()
