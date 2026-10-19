import getpass
import os
from datetime import datetime


def generate_id(prefix, existing_items, id_field):
    """Create the next ID like U001, U002 based on the highest existing number."""
    max_num = 0
    for item in existing_items:
        value = item.get(id_field, "")
        number_part = value[len(prefix):]
        if value.startswith(prefix) and number_part.isdigit():
            max_num = max(max_num, int(number_part))
    return f"{prefix}{max_num + 1:03d}"


def get_input(prompt, validator=None, secret=False):
    """
    Ask until the input is valid.
    validator: function(value) -> (is_valid: bool, message: str)
    secret: hide typing (for passwords)
    """
    while True:
        if secret:
            value = getpass.getpass(prompt)
        else:
            value = input(prompt).strip()

        if validator is None:
            return value

        is_valid, message = validator(value)
        if is_valid:
            return value
        print(f"  ! {message}")


def get_choice(prompt, options):
    """Show a numbered menu and return the chosen option text."""
    while True:
        print(f"\n{prompt}")
        for number, option in enumerate(options, start=1):
            print(f"  {number}. {option}")

        raw = input("Choose an option: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("  ! Invalid choice. Enter one of the numbers shown.")


def format_price(amount):
    return f"${amount:.2f}"


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")