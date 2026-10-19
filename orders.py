from config import ORDERS_FILE, INVENTORY_FILE
from customization import calculate_ingredient_usage, pretty
from menu import load_inventory
from storage import load_json, save_json
from utils import generate_id, now_iso, format_price


# ---------- Load ----------

def load_orders():
    data = load_json(ORDERS_FILE, {"orders": []})
    if "orders" not in data:
        data = {"orders": []}
    return data


# ---------- Inventory ----------

def deduct_inventory(usage):
    """
    Reduce stock by the ingredients the order used.
    Stock never goes below 0, and ingredients not in inventory.json are skipped.
    """
    inventory = load_inventory()
    stock = inventory["ingredients"]

    for ingredient, quantity in usage.items():
        if ingredient in stock:
            stock[ingredient] = max(0, stock[ingredient] - quantity)

    save_json(INVENTORY_FILE, inventory)


# ---------- Create ----------

def create_order(user, drink, selection, total, payment):
    """
    Save a paid order to orders.json, then deduct stock.
    Returns the saved order dict.
    """
    data = load_orders()
    usage = calculate_ingredient_usage(drink, selection)

    order = {
        "order_id": generate_id("O", data["orders"], "order_id"),
        "user_id": user["user_id"],
        "drink_id": drink["drink_id"],
        "drink_name": drink["name"],
        "customization": selection,
        "total_price": total,
        "payment": payment,
        "ingredients_used": usage,
        "timestamp": now_iso(),
    }

    data["orders"].append(order)
    save_json(ORDERS_FILE, data)   # 1. record the transaction
    deduct_inventory(usage)        # 2. then reduce stock
    return order


# ---------- Read ----------

def get_user_orders(user_id):
    """All orders of one user, newest first."""
    orders = [o for o in load_orders()["orders"] if o["user_id"] == user_id]
    return list(reversed(orders))


# ---------- Display ----------

def describe_customization(selection):
    """One-line text for a customization dict."""
    parts = []
    if selection.get("milk"):
        parts.append(f"Milk: {pretty(selection['milk'])}")
    if selection.get("strength"):
        parts.append(f"Strength: {pretty(selection['strength'])}")
    parts.append(f"Temp: {pretty(selection['temperature'])}")

    syrup = selection.get("syrup", {})
    if syrup:
        parts.append("Syrup: " + ", ".join(
            f"{pretty(f)} x{p}" for f, p in syrup.items()
        ))
    return " | ".join(parts)


def print_order_confirmation(order):
    print(f"\nOrder {order['order_id']} recorded. Enjoy your {order['drink_name']}!")


def display_order_history(user_id):
    """Print every order of the user, newest first, with a total at the end."""
    orders = get_user_orders(user_id)

    print("\n=== Order History ===")
    if not orders:
        print("You have no orders yet.")
        return

    for order in orders:
        payment = order["payment"]
        method = pretty(payment["method"])
        if payment["method"] == "card":
            method += f" (**** {payment['card_last4']})"

        print("\n" + "-" * 44)
        print(f"  {order['order_id']}   {order['timestamp'].replace('T', ' ')}")
        print(f"  {order['drink_name']}  -  {format_price(order['total_price'])}")
        print(f"  {describe_customization(order['customization'])}")
        print(f"  Paid by {method}   Ref: {payment['reference']}")

    total_spent = sum(o["total_price"] for o in orders)
    print("\n" + "=" * 44)
    print(f"  {len(orders)} order(s), total spent: {format_price(total_spent)}")
    print("=" * 44)