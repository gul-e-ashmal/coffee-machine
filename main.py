from auth import login_user, register_user
from menu import browse_menu
from orders import create_order, display_order_history, print_order_confirmation
from recipes import prompt_save_recipe, recipes_menu
from session import session
from utils import get_choice


def guest_menu():
    """Shown when nobody is logged in. Returns False when the user exits."""
    choice = get_choice("=== Coffee Ordering System ===", ["Register", "Login", "Exit"])

    if choice == "Register":
        register_user()
    elif choice == "Login":
        login_user()
    else:
        print("\nGoodbye!")
        return False
    return True


def place_order_flow():
    """Browse, customize and pay; then record the order and update stock."""
    result = browse_menu()
    if result is None:
        return

    drink, selection, total, payment = result
    user = session.current_user
    order = create_order(user, drink, selection, total, payment)
    print_order_confirmation(order)

    # FR04: offer to keep this customization as a named recipe
    answer = get_choice("Save this drink as a recipe?", ["Yes", "No"])
    if answer == "Yes":
        prompt_save_recipe(user, drink, selection)


def user_menu():
    """Shown after login."""
    user = session.current_user
    choice = get_choice(
        f"=== Main Menu (logged in as {user['username']}) ===",
        ["Browse Menu and Order",
         "My Recipes",
         "Order History",
         "Logout"],
    )

    if choice == "Browse Menu and Order":
        place_order_flow()
    elif choice == "My Recipes":
        recipes_menu(user)
    elif choice == "Order History":
        display_order_history(user["user_id"])
    elif choice == "Logout":
        session.logout()
        print("\nYou have been logged out.")
    else:
        print("\nThis feature is not built yet.")


def main():
    running = True
    try:
        while running:
            if session.is_logged_in():
                user_menu()
            else:
                running = guest_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")


if __name__ == "__main__":
    main()