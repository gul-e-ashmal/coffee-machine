import hashlib
import hmac
import re
import secrets

from config import (
    USERS_FILE,
    MIN_USERNAME_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MAX_LOGIN_ATTEMPTS,
)
from session import session
from storage import load_json, save_json
from utils import generate_id, get_input, now_iso


# ---------- Helpers ----------

def hash_password(password, salt):
    """Return a salted hash of the password (PBKDF2-HMAC-SHA256)."""
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return digest.hex()


def load_users():
    return load_json(USERS_FILE, {"users": []})


def find_user(username):
    """Find a user by username (case-insensitive). Returns the user dict or None."""
    data = load_users()
    for user in data["users"]:
        if user["username"].lower() == username.lower():
            return user
    return None


def username_exists(username):
    return find_user(username) is not None


# ---------- Validation ----------

def validate_username(username):
    if not (MIN_USERNAME_LENGTH <= len(username) <= MAX_USERNAME_LENGTH):
        return False, (
            f"Username must be {MIN_USERNAME_LENGTH}-{MAX_USERNAME_LENGTH} characters."
        )
    if not re.fullmatch(r"[A-Za-z0-9_]+", username):
        return False, "Username may only contain letters, numbers and underscores."
    return True, ""


def validate_password(password):
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return False, "Password must contain at least one letter and one number."
    return True, ""


# ---------- FR01: Register ----------

def register_user():
    print("\n=== Register ===")

    def check_username(value):
        is_valid, message = validate_username(value)
        if not is_valid:
            return False, message
        if username_exists(value):
            return False, "That username is already taken."
        return True, ""

    username = get_input("Choose a username: ", check_username)
    password = get_input("Choose a password: ", validate_password, secret=True)

    while True:
        confirm = get_input("Confirm password: ", secret=True)
        if confirm == password:
            break
        print("  ! Passwords do not match. Try again.")

    data = load_users()
    salt = secrets.token_hex(16)
    user = {
        "user_id": generate_id("U", data["users"], "user_id"),
        "username": username,
        "password_hash": hash_password(password, salt),
        "salt": salt,
        "created_at": now_iso(),
    }
    data["users"].append(user)
    save_json(USERS_FILE, data)

    print(f"\nAccount created! Your user ID is {user['user_id']}. You can now log in.")
    return user


# ---------- FR02: Login ----------

def login_user():
    print("\n=== Login ===")

    for attempt in range(MAX_LOGIN_ATTEMPTS):
        username = get_input("Username: ")
        password = get_input("Password: ", secret=True)

        user = find_user(username)
        if user is not None:
            expected = user["password_hash"]
            actual = hash_password(password, user["salt"])
            if hmac.compare_digest(expected, actual):
                session.login(user)
                print(f"\nWelcome back, {user['username']}!")
                return user

        remaining = MAX_LOGIN_ATTEMPTS - attempt - 1
        if remaining > 0:
            print(f"  ! Invalid username or password. {remaining} attempt(s) left.")

    print("  ! Too many failed attempts. Returning to main menu.")
    return None