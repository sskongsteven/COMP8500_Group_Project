try:
    # Import the order core functions
    import order as ord_core
except ImportError:
    ord_core = None
    print("Warning: order.py module was not detected in the current path. Running in Mock Mode.")

def display_order_menu():
    """
    Handles numerical inputs and integrates directly with order lifecycle functions.
    """
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
            print("\n--- [Action] View Order Details ---")
            order_id = input("Enter unique Order ID (e.g., O001): ").strip()
            if ord_core:
                try:
                    # Invoke order.py logic to fetch the nested dictionary structure
                    order_data = ord_core.view_order_details(order_id)
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
            else:
                print(f"[Mock Mode] Rendering mock properties for simulated order ID: {order_id}")

        elif choice == '2':
            print("\n--- [Action] Mark Order as Packed ---")
            order_id = input("Enter Order ID to mark as Packed: ").strip()
            if ord_core:
                try:
                    # Trigger state mutation via order.py
                    updated_order = ord_core.update_order_status(order_id, ord_core.STATUS_PACKED)
                    print(f"Success: Order {updated_order['order_id']} status updated to: {updated_order['status']}")
                except ValueError as e:
                    print(f"Transition Rejected: {e}")
            else:
                print(f"[Mock Mode] Order {order_id} marked as Packed dynamically.")

        elif choice == '3':
            print("\n--- [Action] Update Order Status ---")
            order_id = input("Enter Target Order ID: ").strip()
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
                    # Route transition inputs directly into order.py validator matrix
                    updated_order = ord_core.update_order_status(order_id, new_status)
                    print(f"Success: Order {updated_order['order_id']} successfully updated to: {updated_order['status']}")
                except ValueError as e:
                    print(f"Update Aborted: {e}")
            else:
                print(f"[Mock Mode] Order {order_id} updated to status: {new_status}")

        elif choice == '4':
            print("\n--- [Action] Cancel a Pending Order ---")
            order_id = input("Enter Order ID to execute Cancellation: ").strip()
            if ord_core:
                try:
                    # Enforce Rule 6 & 7: Only Pending orders can transition to Cancelled
                    updated_order = ord_core.update_order_status(order_id, ord_core.STATUS_CANCELLED)
                    print(f"Success: Order {updated_order['order_id']} cancelled. Current state: {updated_order['status']}")
                except ValueError as e:
                    print(f"Cancellation Refused: {e}")
            else:
                print(f"[Mock Mode] Pending order {order_id} cancelled successfully.")

        elif choice == '5':
            print("\nExiting sub-menu hierarchy. Returning to main console loop.")
            break
            
        else:
            print("Selection Rejected: Invalid command token. Please select an option bounded between 1 and 5.")

if __name__ == "__main__":
    display_order_menu()
