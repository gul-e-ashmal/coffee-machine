import copy

from config import (
    MILK_OPTIONS,
    STRENGTH_OPTIONS,
    EXTRA_SHOT_PRICE,
    TEMPERATURE_OPTIONS,
    SYRUP_OPTIONS,
    SYRUP_MAX_PER_FLAVOR,
    SYRUP_MAX_TOTAL,
)
from utils import get_choice, get_input, format_price


# ---------- Which options apply to a drink ----------

def supports_milk(drink):
    return "milk_ml" in drink["ingredients"]


def supports_strength(drink):
    return "espresso_shot" in drink["ingredients"]


def default_selection(drink):
    """The starting selection: standard drink with no extras."""
    return {
        "milk": "whole" if supports_milk(drink) else None,
        "strength": "regular" if supports_strength(drink) else None,
        "temperature": "iced" if drink["name"].lower().startswith("iced") else "hot",
        "syrup": {},
    }


# ---------- Validation, price, inventory usage ----------

def validate_selection(drink, selection):
    """Check a selection is allowed for this drink. Returns (is_valid, message)."""
    if supports_milk(drink):
        if selection.get("milk") not in MILK_OPTIONS:
            return False, "Invalid milk type."
    elif selection.get("milk") is not None:
        return False, "This drink has no milk option."

    if supports_strength(drink):
        if selection.get("strength") not in STRENGTH_OPTIONS:
            return False, "Invalid strength."
    elif selection.get("strength") is not None:
        return False, "This drink has no strength option."

    if selection.get("temperature") not in TEMPERATURE_OPTIONS:
        return False, "Invalid temperature."

    syrup = selection.get("syrup", {})
    total = 0
    for flavor, pumps in syrup.items():
        if flavor not in SYRUP_OPTIONS:
            return False, f"Unknown syrup: {flavor}."
        if not isinstance(pumps, int) or not (1 <= pumps <= SYRUP_MAX_PER_FLAVOR):
            return False, f"Syrup pumps must be 1-{SYRUP_MAX_PER_FLAVOR}."
        total += pumps
    if total > SYRUP_MAX_TOTAL:
        return False, f"At most {SYRUP_MAX_TOTAL} syrup pumps in total."

    return True, ""


def calculate_price(drink, selection):
    """Base price plus the add-ons for the selected options."""
    price = drink["base_price"]

    if selection.get("milk"):
        price += MILK_OPTIONS[selection["milk"]]

    if selection.get("strength"):
        price += STRENGTH_OPTIONS[selection["strength"]] * EXTRA_SHOT_PRICE

    for flavor, pumps in selection.get("syrup", {}).items():
        price += SYRUP_OPTIONS[flavor] * pumps

    return round(price, 2)


def calculate_ingredient_usage(drink, selection):
    """
    Ingredients this exact drink consumes (used by FR08 and FR19).
    Starts from the standard recipe and adds extra shots and syrup pumps.
    """
    usage = dict(drink["ingredients"])

    if selection.get("strength"):
        extra_shots = STRENGTH_OPTIONS[selection["strength"]]
        usage["espresso_shot"] = usage.get("espresso_shot", 0) + extra_shots

    for flavor, pumps in selection.get("syrup", {}).items():
        usage[f"syrup_{flavor}"] = pumps

    return usage


# ---------- Display ----------

def pretty(text):
    return text.replace("_", " ").title()


def option_label(name, add_on):
    label = pretty(name)
    if add_on:
        label += f" (+{format_price(add_on)})"
    return label


def show_live_summary(drink, selection):
    """Print the current drink and running price. Called after every change."""
    print("\n" + "=" * 36)
    print(f"  {drink['name']}")
    print("-" * 36)
    if selection["milk"]:
        print(f"  Milk        : {pretty(selection['milk'])}")
    if selection["strength"]:
        print(f"  Strength    : {pretty(selection['strength'])}")
    print(f"  Temperature : {pretty(selection['temperature'])}")

    if selection["syrup"]:
        syrup_text = ", ".join(
            f"{pretty(f)} x{p}" for f, p in selection["syrup"].items()
        )
    else:
        syrup_text = "None"
    print(f"  Syrup       : {syrup_text}")

    print("-" * 36)
    print(f"  Price       : {format_price(calculate_price(drink, selection))}")
    print("=" * 36)


# ---------- One function per option ----------

def choose_milk(drink, selection):
    keys = list(MILK_OPTIONS)
    labels = [option_label(k, MILK_OPTIONS[k]) for k in keys]
    choice = get_choice("Milk type:", labels)
    selection["milk"] = keys[labels.index(choice)]


def choose_strength(drink, selection):
    keys = list(STRENGTH_OPTIONS)
    labels = [
        option_label(k, STRENGTH_OPTIONS[k] * EXTRA_SHOT_PRICE) for k in keys
    ]
    choice = get_choice("Strength (extra espresso shots):", labels)
    selection["strength"] = keys[labels.index(choice)]


def choose_temperature(drink, selection):
    labels = [pretty(t) for t in TEMPERATURE_OPTIONS]
    choice = get_choice("Temperature:", labels)
    selection["temperature"] = TEMPERATURE_OPTIONS[labels.index(choice)]


def choose_syrup(drink, selection):
    """Add syrup pumps flavor by flavor, with a live summary after each change."""
    flavors = list(SYRUP_OPTIONS)

    while True:
        labels = [
            f"{pretty(f)} (+{format_price(SYRUP_OPTIONS[f])} per pump) "
            f"- now: {selection['syrup'].get(f, 0)}"
            for f in flavors
        ] + ["Done with syrups"]

        choice = get_choice("Syrup shots:", labels)
        if choice == "Done with syrups":
            return

        flavor = flavors[labels.index(choice)]
        used_by_others = sum(
            p for f, p in selection["syrup"].items() if f != flavor
        )
        max_allowed = min(SYRUP_MAX_PER_FLAVOR, SYRUP_MAX_TOTAL - used_by_others)

        if max_allowed == 0:
            print(f"  ! The {SYRUP_MAX_TOTAL}-pump limit is reached. "
                  f"Lower another syrup first.")
            continue

        def check_pumps(value, limit=max_allowed):
            if value.isdigit() and 0 <= int(value) <= limit:
                return True, ""
            return False, f"Enter a number from 0 to {limit}."

        pumps = int(get_input(
            f"Pumps of {pretty(flavor)} (0-{max_allowed}): ", check_pumps
        ))

        if pumps == 0:
            selection["syrup"].pop(flavor, None)
        else:
            selection["syrup"][flavor] = pumps

        show_live_summary(drink, selection)


# ---------- Main customization flow ----------

def customize_drink(drink, selection=None):
    """
    Walk the user through the options with a live summary after each step.
    `selection` lets FR05 (edit recipe) start from an existing selection.
    Returns the final selection dict, or None if the user cancels.
    """
    selection = copy.deepcopy(selection) if selection else default_selection(drink)

    # Only the options that make sense for this drink
    steps = []
    if supports_milk(drink):
        steps.append(("Milk type", choose_milk))
    if supports_strength(drink):
        steps.append(("Strength", choose_strength))
    steps.append(("Temperature", choose_temperature))
    steps.append(("Syrup", choose_syrup))

    print(f"\n--- Customize your {drink['name']} ---")
    show_live_summary(drink, selection)

    for _, step in steps:
        step(drink, selection)
        show_live_summary(drink, selection)

    while True:
        choice = get_choice(
            "What would you like to do?",
            ["Confirm drink", "Change an option", "Cancel"],
        )

        if choice == "Confirm drink":
            is_valid, message = validate_selection(drink, selection)
            if is_valid:
                return selection
            print(f"  ! {message}")

        elif choice == "Change an option":
            names = [name for name, _ in steps]
            which = get_choice("Which option?", names)
            steps[names.index(which)][1](drink, selection)
            show_live_summary(drink, selection)

        else:
            print("\nCustomization cancelled.")
            return None