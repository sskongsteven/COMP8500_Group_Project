# ================================================================
# E-Shop Logistics Management System
# Main Menu Module
# Prepared by Louis
# Purpose: Provide the main entry point to the system and direct
#          users to the Inventory, Order & Fulfilment, and
#          Delivery & Tracking modules.
# ================================================================

# Import the Inventory Menu module developed in Increment 1.
from inventory_menu import display_inventory_menu

# Future imports (to be enabled after the corresponding modules are completed 
# in Increment 2 and Increment 3).
# from order_menu import display_order_menu
# from delivery_menu import display_delivery_menu

# Temporary function used until the Order & Fulfilment Module is implemented.
def display_order_menu():
    """
    Placeholder.
    Will be replaced by Increment 2 code.
    """
    print("\nOrder & Fulfilment Module is under development.")

# Temporary function used until the Delivery & Tracking Module is implemented.
def display_delivery_menu():
    """
    Placeholder.
    Will be replaced by Increment 3 code.
    """
    print("\nDelivery & Tracking Module is under development.")

# Display the system main menu and route users to the selected module.
def display_main_menu():
    # Keep displaying the menu until the user exits.
    while True:
        # Display system menu.
        print("\n========================================")
        print(" E-Shop Logistics Management System")
        print("========================================")
        print("1. Product & Inventory Management")
        print("2. Order & Fulfilment Management")
        print("3. Delivery & Tracking Management")
        print("0. Exit")
        print("========================================")
        # Read the user's menu selection.
        choice = input("Please enter your selection: ").strip()
        # Open Inventory Menu.
        if choice == "1":
            display_inventory_menu()
        # Open Order & Fulfilment Menu.
        elif choice == "2":
            display_order_menu()
        # Open Delivery & Tracking Menu.
        elif choice == "3":
            display_delivery_menu()
        # Exit the system.
        elif choice == "0":
            print("\nThank you for using the system.")
            break
        # Handle invalid menu selections.
        else:
            print(
                "\nInvalid option. "
                "Please select a number from the menu."
            )
# Start the application when main_menu.py is executed directly.
if __name__ == "__main__":
    display_main_menu()
