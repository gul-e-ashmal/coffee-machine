import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

USERS_FILE = os.path.join(DATA_DIR, "users.json")
MENU_FILE = os.path.join(DATA_DIR, "menu.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
RECIPES_FILE = os.path.join(DATA_DIR, "recipes.json")

# Validation rules
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 20
MIN_PASSWORD_LENGTH = 6

# Login
MAX_LOGIN_ATTEMPTS = 3

# Customization options (keys are stored in orders.json and recipes.json).
# Values are the price add-ons.
MILK_OPTIONS = {"whole": 0.00, "skim": 0.00, "soy": 0.40, "oat": 0.50, "almond": 0.50}

# Strength = number of EXTRA espresso shots added to the drink's normal recipe
STRENGTH_OPTIONS = {"regular": 0, "strong": 1, "extra_strong": 2}
EXTRA_SHOT_PRICE = 0.60

TEMPERATURE_OPTIONS = ["hot", "warm", "iced"]

# Syrup flavors with the price per pump
SYRUP_OPTIONS = {"vanilla": 0.40, "caramel": 0.40, "hazelnut": 0.40}
SYRUP_MAX_PER_FLAVOR = 3
SYRUP_MAX_TOTAL = 4

# Recipes
MIN_RECIPE_NAME_LENGTH = 3
MAX_RECIPE_NAME_LENGTH = 30
MAX_RECIPES_PER_USER = 20