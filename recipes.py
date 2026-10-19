import re

from config import (
    RECIPES_FILE,
    MIN_RECIPE_NAME_LENGTH,
    MAX_RECIPE_NAME_LENGTH,
    MAX_RECIPES_PER_USER,
)
from customization import customize_drink, calculate_price
from menu import load_menu, select_category, select_drink
from orders import describe_customization
from storage import load_json, save_json
from utils import generate_id, get_choice, get_input, now_iso, format_price


# ---------- Load and find ----------

def load_recipes():
    data = load_json(RECIPES_FILE, {"recipes": []})
    if "recipes" not in data:
        data = {"recipes": []}
    return data


def get_user_recipes(user_id):
    """All recipes of one user, oldest first."""
    return [r for r in load_recipes()["recipes"] if r["user_id"] == user_id]


def find_drink(drink_id):
    """Look a drink up in the menu by ID. Returns the drink dict or None."""
    for category in load_menu().get("categories", []):
        for drink in category.get("drinks", []):
            if drink["drink_id"] == drink_id:
                return drink
    return None


# ---------- Validation ----------

def normalize_name(name):
    """Trim and collapse repeated spaces: '  My   Latte ' -> 'My Latte'."""
    return " ".join(name.split())


def recipe_name_exists(user_id, name, ignore_recipe_id=None):
    """Case-insensitive duplicate check within ONE user's recipes."""
    wanted = normalize_name(name).lower()
    for recipe in get_user_recipes(user_id):
        if recipe["recipe_id"] == ignore_recipe_id:
            continue
        if recipe["name"].lower() == wanted:
            return True
    return False


def validate_recipe_name(name):
    name = normalize_name(name)
    if not (MIN_RECIPE_NAME_LENGTH <= len(name) <= MAX_RECIPE_NAME_LENGTH):
        return False, (
            f"Name must be {MIN_RECIPE_NAME_LENGTH}-{MAX_RECIPE_NAME_LENGTH} characters."
        )
    if not re.fullmatch(r"[A-Za-z0-9 '\-]+", name):
        return False, "Use only letters, numbers, spaces, hyphens and apostrophes."
    return True, ""


# ---------- FR04: Save ----------

def save_recipe(user, drink, selection, name):
    """Write a named recipe to recipes.json. Returns the saved recipe dict."""
    data = load_recipes()
    timestamp = now_iso()

    recipe = {
        "recipe_id": generate_id("R", data["recipes"], "recipe_id"),
        "user_id": user["user_id"],
        "name": normalize_name(name),
        "drink_id": drink["drink_id"],
        "customization": selection,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    data["recipes"].append(recipe)
    save_json(RECIPES_FILE, data)
    return recipe


def prompt_save_recipe(user, drink, selection):
    """
    Ask for a name and save the drink as a recipe.
    Returns the saved recipe, or None if the user cancels or the limit is reached.
    """
    if len(get_user_recipes(user["user_id"])) >= MAX_RECIPES_PER_USER:
        print(f"\n  ! You already have {MAX_RECIPES_PER_USER} recipes. "
              f"Delete one before saving another.")
        return None

    def check_name(value):
        if value.lower() == "c":
            return True, ""
        is_valid, message = validate_recipe_name(value)
        if not is_valid:
            return False, message
        if recipe_name_exists(user["user_id"], value):
            return False, "You already have a recipe with that name."
        return True, ""

    print(f"\n--- Save your {drink['name']} as a recipe ---")
    print(f"  {describe_customization(selection)}")
    name = get_input("Recipe name ('c' to cancel): ", check_name)

    if name.lower() == "c":
        print("\nRecipe not saved.")
        return None

    recipe = save_recipe(user, drink, selection, name)
    print(f"\nRecipe '{recipe['name']}' saved ({recipe['recipe_id']}).")
    return recipe


# ---------- Create from the recipes menu ----------

def create_recipe_flow(user):
    """Build a drink (category, drink, customize) and save it without paying."""
    while True:
        category = select_category()
        if category is None:
            return None

        drink = select_drink(category)
        if drink is None:
            continue  # back to the category list

        selection = customize_drink(drink)
        if selection is None:
            continue  # cancelled: back to the category list

        return prompt_save_recipe(user, drink, selection)


# ---------- Display ----------

def display_recipes(user_id):
    """Print the user's saved recipes. Returns the list of recipes shown."""
    recipes = get_user_recipes(user_id)

    print("\n=== My Recipes ===")
    if not recipes:
        print("You have no saved recipes yet.")
        return recipes

    for number, recipe in enumerate(recipes, start=1):
        drink = find_drink(recipe["drink_id"])
        print("\n" + "-" * 44)
        if drink is None:
            print(f"  {number}. {recipe['name']}  ({recipe['recipe_id']})")
            print("     This drink is no longer on the menu.")
            continue

        price = calculate_price(drink, recipe["customization"])
        print(f"  {number}. {recipe['name']}  ({recipe['recipe_id']})")
        print(f"     {drink['name']}  -  {format_price(price)}")
        print(f"     {describe_customization(recipe['customization'])}")
    print("-" * 44)
    return recipes


# ---------- Recipes menu ----------

def recipes_menu(user):
    """Submenu opened from 'My Recipes' in the main menu."""
    while True:
        choice = get_choice(
            "=== My Recipes ===",
            ["View my recipes", "Create a new recipe", "Edit a recipe", "Back"],
        )

        if choice == "View my recipes":
            display_recipes(user["user_id"])
        elif choice == "Create a new recipe":
            create_recipe_flow(user)
        elif choice == "Edit a recipe":
            edit_recipe_flow(user)
        else:
            return


# ---------- FR05: Modify ----------

def get_recipe(user_id, recipe_id):
    """Return one recipe if it belongs to this user, else None."""
    for recipe in get_user_recipes(user_id):
        if recipe["recipe_id"] == recipe_id:
            return recipe
    return None


def update_recipe(user_id, recipe_id, name=None, customization=None):
    """
    Change the name and/or customization of a recipe and save the file.
    Only the owner can update a recipe. updated_at is refreshed;
    created_at, recipe_id, user_id and drink_id never change.
    Returns the updated recipe, or None if it wasn't found.
    """
    data = load_recipes()

    for recipe in data["recipes"]:
        if recipe["recipe_id"] == recipe_id and recipe["user_id"] == user_id:
            if name is not None:
                recipe["name"] = normalize_name(name)
            if customization is not None:
                recipe["customization"] = customization
            recipe["updated_at"] = now_iso()
            save_json(RECIPES_FILE, data)
            return recipe

    return None


def show_recipe_summary(recipe):
    """Print one recipe with its drink, current price and customization."""
    drink = find_drink(recipe["drink_id"])
    print("\n" + "-" * 44)
    print(f"  {recipe['name']}  ({recipe['recipe_id']})")
    if drink is None:
        print("  This drink is no longer on the menu.")
    else:
        price = calculate_price(drink, recipe["customization"])
        print(f"  {drink['name']}  -  {format_price(price)}")
        print(f"  {describe_customization(recipe['customization'])}")
    print("-" * 44)


def rename_recipe(user, recipe):
    """Ask for a new name and save it. Returns True if the name changed."""
    def check_name(value):
        if value.lower() == "c":
            return True, ""
        is_valid, message = validate_recipe_name(value)
        if not is_valid:
            return False, message
        # ignore_recipe_id lets a recipe keep or re-case its own name
        if recipe_name_exists(user["user_id"], value, ignore_recipe_id=recipe["recipe_id"]):
            return False, "You already have another recipe with that name."
        return True, ""

    new_name = get_input("New name ('c' to cancel): ", check_name)

    if new_name.lower() == "c":
        print("\nRename cancelled.")
        return False

    if normalize_name(new_name) == recipe["name"]:
        print("\nThat is already the recipe's name. No changes made.")
        return False

    update_recipe(user["user_id"], recipe["recipe_id"], name=new_name)
    print(f"\nRecipe renamed to '{normalize_name(new_name)}'.")
    return True


def change_recipe_customization(user, recipe):
    """Re-open the FR15 customization flow on the saved choices and save the result."""
    drink = find_drink(recipe["drink_id"])
    if drink is None:
        print("\n  ! This drink is no longer on the menu, so it can't be customized.")
        return False

    new_selection = customize_drink(drink, recipe["customization"])

    if new_selection is None:
        print("\nNo changes were saved.")
        return False

    if new_selection == recipe["customization"]:
        print("\nYou did not change anything. No changes made.")
        return False

    update_recipe(user["user_id"], recipe["recipe_id"], customization=new_selection)
    print(f"\nCustomization saved. New price: "
          f"{format_price(calculate_price(drink, new_selection))}")
    return True


def edit_recipe(user, recipe_id):
    """Edit menu for one recipe. Reloads the recipe after each change."""
    while True:
        recipe = get_recipe(user["user_id"], recipe_id)
        if recipe is None:
            print("\n  ! That recipe could not be found.")
            return

        show_recipe_summary(recipe)
        choice = get_choice(
            "What would you like to change?",
            ["Rename", "Change customization", "Done"],
        )

        if choice == "Rename":
            rename_recipe(user, recipe)
        elif choice == "Change customization":
            change_recipe_customization(user, recipe)
        else:
            return


def select_recipe(user_id):
    """Let the user pick one of their recipes. Returns its recipe_id or None."""
    recipes = get_user_recipes(user_id)
    if not recipes:
        print("\nYou have no saved recipes yet.")
        return None

    labels = []
    for recipe in recipes:
        drink = find_drink(recipe["drink_id"])
        drink_name = drink["name"] if drink else "drink removed"
        labels.append(f"{recipe['name']} ({drink_name})")
    labels.append("Back")

    choice = get_choice("Which recipe do you want to edit?", labels)
    if choice == "Back":
        return None
    return recipes[labels.index(choice)]["recipe_id"]


def edit_recipe_flow(user):
    """Pick a recipe, then edit it. Repeats until the user goes back."""
    while True:
        recipe_id = select_recipe(user["user_id"])
        if recipe_id is None:
            return
        edit_recipe(user, recipe_id)