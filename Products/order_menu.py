try:
    # Import the order functions from order.py
    import order as ord_core
except ImportError:
    ord_core = None
    print("Warning: order.py module was not detected. Running in Mock Mode.")

def select_order_from_list():
    """
    Helper function to render existing records as a numbered console list.
    Added 'Option 0' to allow navigation rollback.
    """
    if not ord_core:
        print("[Mock Mode] Staged order collection placeholder.")
        return None
        
    orders = ord_core.list_orders()
    if not orders:
        print("Notification: There are currently no active orders stored in the JSON file.")
        return None
        
    print("\n--- Available Orders List ---")
    # Loop through the rows and append a numbered visual index (1, 2, 3...)
    for idx, order in enumerate(orders, 1):
        print(f"[{idx}] Order ID: {order['order_id']} | Customer: {order['customer_name']} | Status: {order['status']} | Total: ${order['total']}")
    print("[0] Return to Order Menu (Cancel and Go Back)")
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

def display_order_menu():
    """Renders the primary text-based order fulfillment control sub-menu with secondary loop flows."""
    while True:
        print("\n==================================")
        print("    E-Shop Order & Fulfillment    ")
        print("==================================")
        print("1. View Order Details")
        print("2. Mark Order as Packed")
        print("3. Update Order Status")
        print("4. Cancel a Pending Order")
        print("5. Return to Main Menu")
        print("==================================")
        
        choice = input("Please enter your selection (1-5): ").strip()
        
        if choice == '1':
            
            while True:
                print("\n--- [Action] View Order Details ---")
                selected_id = select_order_from_list()
                
                if selected_id == "BACK":
                    break # Break the sub-loop and return to the main order menu
                    
                if selected_id and ord_core:
                    try:
                        order_data = ord_core.view_order_details(selected_id)
                        print("\n[Order Data Schema Details]")
                        print(f"Order ID        : {order_data['order_id']}")
                        print(f"Customer Name   : {order_data['customer_name']}")
                        print(f"Delivery Address: {order_data['delivery_address']}")
                        print(f"Created At      : {order_data['created_at']}")
                        print(f"Current Status  : {order_data['status']}")
                        print(f"Order Total     : ${order_data['total']}")
                        print("Items Ordered   :")
                        for item in order_data['items']:
                            print(f"  - [{item['product_id']}] {item['product_name']} | Qty: {item['quantity']} | Line Total: ${item['line_total']}")
                        print("Status History Tracking (Audit Trail):")
                        for history in order_data['status_history']:
                            print(f"  - [{history['at']}] Status changed to: {history['status']}")
                    except ValueError as e:
                        print(f"Query Denied: {e}")
                
                # Ask user if they want to view another order before returning to main list
                another = input("\nDo you want to view another order? (y/n): ").strip().lower()
                if another != 'y' and another != 'yes':
                    break # Safe break out of the inquiry loop

        elif choice == '2':
            print("\n--- [Action] Mark Order as Packed ---")
            selected_id = select_order_from_list()
            if selected_id == "BACK":
                continue
            if selected_id and ord_core:
                try:
                    updated_order = ord_core.update_order_status(selected_id, ord_core.STATUS_PACKED)
                    print(f"Success: Order {updated_order['order_id']} status updated to: {updated_order['status']}")
                except ValueError as e:
                    print(f"Transition Rejected: {e}")

        elif choice == '3':
            print("\n--- [Action] Update Order Status ---")
            selected_id = select_order_from_list()
            if selected_id == "BACK":
                continue
            if selected_id:
                print("Available Status Choices:")
                print("  1. Ready for Delivery")
                print("  2. Out for Delivery")
                print("  3. Delivered")
                status_choice = input("Select new status option (1-3): ").strip()
                
                new_status = None
                if status_choice == '1':
                    new_status = ord_core.STATUS_READY_FOR_DELIVERY if ord_core else "Ready for Delivery"
                elif status_choice == '2':
                    new_status = ord_core.STATUS_OUT_FOR_DELIVERY if ord_core else "Out for Delivery"
                elif status_choice == '3':
                    new_status = ord_core.STATUS_DELIVERED if ord_core else "Delivered"
                else:
                    print("Invalid operational choice token. Mutation aborted.")
                    continue
                    
                if ord_core:
                    try:
                        updated_order = ord_core.update_order_status(selected_id, new_status)
                        print(f"Success: Order {updated_order['order_id']} successfully updated to: {updated_order['status']}")
                    except ValueError as e:
                        print(f"Update Aborted: {e}")

        elif choice == '4':
            print("\n--- [Action] Cancel a Pending Order ---")
            selected_id = select_order_from_list()
            if selected_id == "BACK":
                continue
            if selected_id and ord_core:
                try:
                    updated_order = ord_core.update_order_status(selected_id, ord_core.STATUS_CANCELLED)
                    print(f"Success: Order {updated_order['order_id']} cancelled. Current state: {updated_order['status']}")
                except ValueError as e:
                    print(f"Cancellation Refused: {e}")

        elif choice == '5':
            print("\nExiting sub-menu hierarchy. Returning to main console loop.")
            break
        else:
            print("Selection Rejected: Invalid command token. Please select an option bounded between 1 and 5.")

if __name__ == "__main__":
    display_order_menu()
