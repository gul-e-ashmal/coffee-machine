import math
import re
import secrets
from datetime import datetime

from utils import get_choice, get_input, format_price

# Simulation rule: any card number ending in these digits is declined.
# This lets you test the failed-payment path without a real bank.
DECLINE_TEST_ENDING = "0000"


# ---------- Helpers ----------

def generate_reference():
    """Unique transaction reference, e.g. TXN-20261018144700-A3F9C1."""
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"TXN-{stamp}-{secrets.token_hex(3).upper()}"


def clean_card_number(value):
    """Remove spaces and dashes so '4111 1111 1111 1111' works."""
    return re.sub(r"[ -]", "", value)


# ---------- Validators (return (is_valid, message)) ----------

def validate_card_number(value):
    if not re.fullmatch(r"\d{16}", clean_card_number(value)):
        return False, "Card number must be exactly 16 digits."
    return True, ""


def validate_expiry(value):
    match = re.fullmatch(r"(\d{2})/(\d{2})", value)
    if not match:
        return False, "Use the format MM/YY, for example 08/29."
    month, year = int(match.group(1)), 2000 + int(match.group(2))
    if not 1 <= month <= 12:
        return False, "Month must be between 01 and 12."
    now = datetime.now()
    if (year, month) < (now.year, now.month):
        return False, "This card has expired."
    return True, ""


def validate_cvv(value):
    if not re.fullmatch(r"\d{3}", value):
        return False, "CVV must be 3 digits."
    return True, ""


# ---------- Payment methods ----------

def pay_by_card(amount):
    """
    Simulated card payment. Asks for number, expiry and CVV.
    Only the last 4 digits are kept in the result; the full number, expiry
    and CVV are never stored.
    Returns a payment result dict (status 'success' or 'failed').
    """
    print("\n--- Card payment (simulated) ---")
    print(f"Amount due: {format_price(amount)}")

    number = clean_card_number(
        get_input("Card number (16 digits): ", validate_card_number)
    )
    get_input("Expiry (MM/YY): ", validate_expiry)
    get_input("CVV (3 digits): ", validate_cvv, secret=True)

    last4 = number[-4:]
    result = {
        "method": "card",
        "amount": amount,
        "card_last4": last4,
    }

    if last4 == DECLINE_TEST_ENDING:
        result.update({"status": "failed", "reference": None,
                       "reason": "Card declined"})
    else:
        result.update({"status": "success", "reference": generate_reference()})
    return result


def pay_by_cash(amount):
    """
    Simulated cash payment. Asks how much cash was handed over and works out
    the change. Returns a payment result dict, or None if the user cancels.
    """
    print("\n--- Cash payment ---")
    print(f"Amount due: {format_price(amount)}")

    def check_cash(value):
        if value.lower() == "c":
            return True, ""
        try:
            number = float(value)
        except ValueError:
            return False, "Enter a number like 10 or 10.50 (or 'c' to cancel)."
        if not math.isfinite(number) or number <= 0:
            return False, "Enter an amount greater than 0."
        return True, ""

    while True:
        raw = get_input("Cash given ('c' to cancel): ", check_cash)
        if raw.lower() == "c":
            return None

        tendered = round(float(raw), 2)
        if tendered < amount:
            print(f"  ! Not enough. {format_price(amount - tendered)} still missing.")
            continue

        return {
            "method": "cash",
            "amount": amount,
            "cash_tendered": tendered,
            "change": round(tendered - amount, 2),
            "status": "success",
            "reference": generate_reference(),
        }


# ---------- Main payment flow ----------

def print_receipt(result):
    print("\n" + "=" * 36)
    print("  PAYMENT SUCCESSFUL")
    print("-" * 36)
    print(f"  Method     : {result['method'].title()}")
    print(f"  Paid       : {format_price(result['amount'])}")
    if result["method"] == "card":
        print(f"  Card       : **** **** **** {result['card_last4']}")
    else:
        print(f"  Cash given : {format_price(result['cash_tendered'])}")
        print(f"  Change     : {format_price(result['change'])}")
    print(f"  Reference  : {result['reference']}")
    print("=" * 36)


def process_payment(amount):
    """
    Let the user pay for an order.
    Returns the payment result dict on success, or None if the user cancels.
    A failed attempt (e.g. declined card) lets the user retry or switch method.
    """
    amount = round(amount, 2)
    print(f"\n=== Payment: {format_price(amount)} ===")

    while True:
        choice = get_choice("Payment method:", ["Card", "Cash", "Cancel order"])

        if choice == "Cancel order":
            return None

        result = pay_by_card(amount) if choice == "Card" else pay_by_cash(amount)

        if result is None:   # cancelled inside the cash screen
            continue

        if result["status"] == "success":
            print_receipt(result)
            return result

        print(f"\n  ! Payment failed: {result['reason']}. "
              f"Try again or choose another method.")