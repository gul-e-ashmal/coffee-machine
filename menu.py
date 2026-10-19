from config import MENU_FILE
from storage import load_json
from customization import customize_drink, calculate_price
from utils import get_choice, format_price
from config import MENU_FILE, INVENTORY_FILE
from customization import (
    customize_drink,
    calculate_price,
    calculate_ingredient_usage,
    pretty,
)
from storage import load_json, save_json
from utils import get_choice, format_price
from payment import process_payment

# Starter menu. It is written to data/menu.json the first time the menu is
# opened. After that, you can edit menu.json by hand to add categories or drinks.
DEFAULT_MENU = {
    "categories": [
        {
            "category_id": "C01",
            "name": "Espresso",
            "drinks": [
                {"drink_id": "D001", "name": "Espresso", "base_price": 2.50,
                 "ingredients": {"espresso_shot": 1}},
                {"drink_id": "D002", "name": "Americano", "base_price": 2.80,
                 "ingredients": {"espresso_shot": 1}},
                {"drink_id": "D003", "name": "Macchiato", "base_price": 3.00,
                 "ingredients": {"espresso_shot": 1, "milk_ml": 30}},
            ],
        },
        {
            "category_id": "C02",
            "name": "Milk Coffee",
            "drinks": [
                {"drink_id": "D004", "name": "Latte", "base_price": 3.50,
                 "ingredients": {"espresso_shot": 1, "milk_ml": 200}},
                {"drink_id": "D005", "name": "Cappuccino", "base_price": 3.40,
                 "ingredients": {"espresso_shot": 1, "milk_ml": 120}},
                {"drink_id": "D006", "name": "Flat White", "base_price": 3.60,
                 "ingredients": {"espresso_shot": 2, "milk_ml": 120}},
            ],
        },
        {
            "category_id": "C03",
            "name": "Tea",
            "drinks": [
                {"drink_id": "D007", "name": "Black Tea", "base_price": 2.20,
                 "ingredients": {"tea_bag": 1}},
                {"drink_id": "D008", "name": "Green Tea", "base_price": 2.20,
                 "ingredients": {"tea_bag": 1}},
                {"drink_id": "D009", "name": "Chai Latte", "base_price": 3.30,
                 "ingredients": {"tea_bag": 1, "milk_ml": 150}},
            ],
        },
        {
            "category_id": "C04",
            "name": "Cold Drinks",
            "drinks": [
                {"drink_id": "D010", "name": "Iced Latte", "base_price": 3.80,
                 "ingredients": {"espresso_shot": 1, "milk_ml": 200}},
                {"drink_id": "D011", "name": "Iced Americano", "base_price": 3.00,
                 "ingredients": {"espresso_shot": 1}},
            ],
        },
    ]
}


def load_menu():
    """Read the menu from menu.json (creates it from DEFAULT_MENU if missing)."""
    return load_json(MENU_FILE, DEFAULT_MENU)

# Starter stock. Written to data/inventory.json the first time it is needed.
DEFAULT_INVENTORY = {
    "ingredients": {
        "espresso_shot": 50,
        "milk_ml": 5000,
        "tea_bag": 40,
        "syrup_vanilla": 20,
        "syrup_caramel": 20,
        "syrup_hazelnut": 20,
    }
}


def load_inventory():
    """Read stock levels from inventory.json (seeded from DEFAULT_INVENTORY)."""
    inventory = load_json(INVENTORY_FILE, DEFAULT_INVENTORY)
    if "ingredients" not in inventory:
        save_json(INVENTORY_FILE, DEFAULT_INVENTORY)
        return DEFAULT_INVENTORY
    return inventory


def ingredient_name(key):
    """'milk_ml' -> 'Milk', 'syrup_vanilla' -> 'Syrup Vanilla'."""
    return pretty(key.replace("_ml", ""))


def find_shortages(usage):
    """
    Compare an ingredient usage dict with the current stock.
    Returns a list of (ingredient, needed, available) for every ingredient that
    is short. An ingredient missing from inventory.json counts as 0 in stock.
    """
    stock = load_inventory()["ingredients"]
    shortages = []
    for ingredient, needed in usage.items():
        available = stock.get(ingredient, 0)
        if available < needed:
            shortages.append((ingredient, needed, available))
    return shortages


def is_drink_available(drink):
    """True if the standard recipe of this drink can be made right now."""
    return not find_shortages(drink["ingredients"])


def get_unavailable_reason(drink):
    """Text naming the ingredients that are too low, e.g. 'Milk, Espresso Shot'."""
    shortages = find_shortages(drink["ingredients"])
    return ", ".join(ingredient_name(name) for name, _, _ in shortages)


def get_categories():
    """Return only the categories that contain at least one drink."""
    menu = load_menu()
    return [c for c in menu.get("categories", []) if c.get("drinks")]


def display_categories(categories):
    """Print the categories as a numbered list with the drink count."""
    print("\n--- Beverage Categories ---")
    for number, category in enumerate(categories, start=1):
        count = len(category["drinks"])
        label = "drink" if count == 1 else "drinks"
        print(f"  {number}. {category['name']} ({count} {label})")


def select_category():
    """
    Let the user pick a category.
    Returns the chosen category dict, or None if the user goes back
    (or if there are no categories).
    """
    categories = get_categories()
    if not categories:
        print("\nNo beverage categories are available right now.")
        return None

    # display_categories(categories)

    labels = [f"{c['name']} ({len(c['drinks'])})" for c in categories] + ["Back"]
    choice = get_choice("Select a category:", labels)

    if choice == "Back":
        return None
    return categories[labels.index(choice)]


def browse_menu():
    """
    Menu flow: category -> drink -> customize -> stock check -> payment.
    Returns (drink, selection, total, payment) when the order is paid,
    otherwise None.
    """
    while True:
        category = select_category()
        if category is None:
            return None

        drink = select_drink(category)
        if drink is None:
            continue  # back to the category list

        selection = customize_drink(drink)

        # Re-check stock for the customized drink (extra shots and syrup)
        while selection is not None:
            usage = calculate_ingredient_usage(drink, selection)
            shortages = find_shortages(usage)
            if not shortages:
                break

            print("\n  ! Sorry, we can't make this drink as customized:")
            for ingredient, needed, available in shortages:
                print(f"    - {ingredient_name(ingredient)}: "
                      f"needs {needed}, only {available} left")

            action = get_choice(
                "What would you like to do?",
                ["Change my customization", "Choose another drink"],
            )
            if action == "Change my customization":
                selection = customize_drink(drink, selection)
            else:
                selection = None

        if selection is None:
            continue  # cancelled or abandoned: back to the category list

        total = calculate_price(drink, selection)
        print(f"\n{drink['name']} confirmed. Total: {format_price(total)}")

        payment = process_payment(total)
        if payment is None:
            print("\nPayment cancelled. Your order was not placed.")
            continue  # back to the category list

        return drink, selection, total, payment



def get_drinks_by_category(category_id):
    """Return the list of drinks for one category ID ([] if not found)."""
    for category in get_categories():
        if category["category_id"] == category_id:
            return category["drinks"]
    return []


def drink_label(drink):
    """Text shown for a drink in the list, e.g. 'Latte - $3.50'."""
    label = f"{drink['name']} - {format_price(drink['base_price'])}"
    if not is_drink_available(drink):
        label += "  [UNAVAILABLE]"
    return label


def select_drink(category):
    """
    Show the drinks of a category and let the user pick one.
    Unavailable drinks are listed but cannot be selected.
    Returns the chosen drink dict, or None if the user goes back.
    """
    drinks = get_drinks_by_category(category["category_id"])
    if not drinks:
        print(f"\nNo drinks are available in '{category['name']}'.")
        return None

    while True:
        labels = [drink_label(d) for d in drinks] + ["Back to categories"]
        choice = get_choice(f"--- {category['name']}: select a drink ---", labels)

        if choice == "Back to categories":
            return None

        drink = drinks[labels.index(choice)]
        if is_drink_available(drink):
            return drink

        print(f"\n  ! {drink['name']} is currently unavailable "
              f"(not enough: {get_unavailable_reason(drink)}).")