# Coffee Ordering System

A terminal-based coffee ordering application written in Python. Users can register, log in, browse a drink menu, customize drinks in real time, pay (simulated), review their order history, and save, edit and re-order their own custom recipes.

There is **no database and no graphical interface**. All data is stored in simple JSON text files inside the `data/` folder, and the whole program runs in a terminal window.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Environment and Prerequisites](#2-environment-and-prerequisites)
3. [Installation Guide (for beginners)](#3-installation-guide-for-beginners)
4. [Execution Guide](#4-execution-guide)
5. [Testing the 10 Functionalities](#5-testing-the-10-functionalities)
6. [Project Structure](#6-project-structure)
7. [Data Files](#7-data-files)
8. [Configuration](#8-configuration)
9. [Troubleshooting](#9-troubleshooting)
10. [Known Limitations](#10-known-limitations)

---

## 1. System Overview

The system simulates a coffee shop ordering kiosk. It covers the full journey from creating an account to receiving an order confirmation.

### Functional requirements implemented

| ID | Functionality | Short description |
|---|---|---|
| FR01 | Register a user account | Create an account with a validated username and password |
| FR02 | Log in | Authenticate with credentials and start a session |
| FR06 | Display beverage categories | Entry point of the menu (Espresso, Milk Coffee, Tea, Cold Drinks) |
| FR07 | Display drinks in a category | Shows drinks and prices of the selected category |
| FR15 | Customize a beverage in real time | Milk type, strength, temperature and syrup shots, with a live price summary |
| FR08 | Disable unavailable drinks | Drinks with low ingredient stock are marked `[UNAVAILABLE]` and cannot be ordered |
| FR18 | Process beverage payments | Simulated card or cash payment (no real money or real card processing) |
| FR19 | Record completed transactions | Saves each order with its customization and updates stock; order history is viewable |
| FR04 | Save and name a custom recipe | Keep a customized drink as a named recipe |
| FR05 | Modify a saved recipe | Rename a recipe or change its customization |

### Bonus feature

- **Order directly from a saved recipe** (My Recipes, then Order from a recipe).

### Key characteristics

- Runs entirely in the terminal (command line).
- Uses only the Python standard library, so **nothing extra needs to be installed**.
- Passwords are salted and hashed (never stored in plain text).
- Only the last 4 digits of a card are ever stored, and the card flow is a simulation.

---

## 2. Environment and Prerequisites

| Requirement | Details |
|---|---|
| Programming language | **Python 3.8 or newer** (Python 3.12 or later is recommended) |
| Python download | https://www.python.org/downloads/ |
| Python documentation | https://docs.python.org/3/ |
| Code editor (optional, recommended) | **Visual Studio Code** (VS Code) |
| VS Code download | https://code.visualstudio.com/download |
| VS Code Python extension | https://marketplace.visualstudio.com/items?itemName=ms-python.python |
| Operating system | Windows 10/11, macOS, or Linux |
| External libraries | **None.** No `pip install` is needed. |
| Database | **None.** Data is stored in JSON files. |
| Internet connection | Only needed to download Python and VS Code. The application itself works offline. |

### Python standard-library modules used (already included with Python)

`json`, `os`, `tempfile`, `hashlib`, `secrets`, `hmac`, `getpass`, `datetime`, `re`, `math`, `copy`

---

## 3. Installation Guide (for beginners)

You do not need any programming experience. Follow the steps in order.

### Step 1: Install Python

1. Open https://www.python.org/downloads/ in your web browser.
2. Click the yellow **Download Python** button and run the installer.
3. **Windows users, important:** on the first installer screen, tick the box **"Add python.exe to PATH"** before clicking **Install Now**.
4. When the installer finishes, click **Close**.

Verify the installation:

1. Open a terminal:
   - **Windows:** press the `Windows` key, type `cmd`, press `Enter`.
   - **macOS:** press `Cmd + Space`, type `Terminal`, press `Enter`.
   - **Linux:** press `Ctrl + Alt + T`.
2. Type the following and press `Enter`:

   ```
   python --version
   ```

   On macOS and Linux you may need to use `python3` instead:

   ```
   python3 --version
   ```

3. You should see something like `Python 3.12.4`. Any version of **3.8 or higher** works.

### Step 2: Install Visual Studio Code (optional but recommended)

1. Open https://code.visualstudio.com/download and download the version for your operating system.
2. Run the installer and accept the defaults.
3. Open VS Code, click the **Extensions** icon in the left bar (four squares), search for **Python** (published by Microsoft), and click **Install**.
   Direct link: https://marketplace.visualstudio.com/items?itemName=ms-python.python

> You can also skip VS Code entirely and run the program from any plain terminal.

### Step 3: Get the project files

Choose one option:

- **Option A: Download as a ZIP.** On the repository page, click **Code**, then **Download ZIP**, and extract it to a folder you can find easily, for example your Desktop.
- **Option B: Use Git.** Install Git from https://git-scm.com/downloads, then run:

  ```
  git clone <repository-url>
  ```

  Replace `<repository-url>` with the link shown on the repository page.

After this step you should have a folder named `coffee_app` containing files such as `main.py`, `config.py` and `auth.py`.

---

## 4. Execution Guide

There are two ways to run the program. Both do exactly the same thing.

### Option A: Run from VS Code

1. Open VS Code.
2. Choose **File**, then **Open Folder...**, and select the `coffee_app` folder.
3. If VS Code asks "Do you trust the authors?", click **Yes, I trust the authors**.
4. Open the integrated terminal: choose **Terminal**, then **New Terminal** (shortcut: `` Ctrl + ` ``).
5. In the terminal, type:

   ```
   python main.py
   ```

   (On macOS or Linux use `python3 main.py` if `python` is not recognized.)

6. The Coffee Ordering System menu appears. Type the number of an option and press `Enter`.

> **Tip:** Run the program with `python main.py` in the terminal, as shown above, rather than the "Run" button. This guarantees that hidden password typing works correctly.

### Option B: Run from a plain terminal

1. Open a terminal (see Step 1 above).
2. Go to the project folder. For example, if it is on your Desktop:

   - **Windows:**
     ```
     cd Desktop\coffee_app
     ```
   - **macOS / Linux:**
     ```
     cd ~/Desktop/coffee_app
     ```

3. Start the program:

   ```
   python main.py
   ```

   (Use `python3 main.py` if needed.)

### How to use the program

- Every menu is a numbered list. **Type the number and press `Enter`.**
- When you type a password or a card CVV, **nothing appears on screen**. This is intentional, so just type and press `Enter`.
- Press `Ctrl + C` at any time to exit the program.
- There is no separate build or compile step. Python runs the files directly.
- Data files in the `data/` folder are **created automatically** on first use.

---

## 5. Testing the 10 Functionalities

Follow these steps in order. Each step builds on the previous one. Tests are done by hand using the terminal.

### Test card numbers (simulation only)

| Purpose | Card number | Expiry | CVV |
|---|---|---|---|
| Successful payment | `4111 1111 1111 1111` | `12/29` | `123` |
| Declined payment | `4111 1111 1111 0000` | `12/29` | `123` |

Never enter a real card number. Any 16 digits are accepted, and a number ending in `0000` is always declined.

---

### FR01: Register a new user account

1. Start the program and choose **Register**.
2. Enter username `sara` and password `coffee1`, then repeat the password.
3. **Expected:** "Account created! Your user ID is U001."
4. Try these invalid inputs. Each should be rejected with a message:
   - Username `sara` again (already taken), also `SARA`.
   - Username `ab` (too short) or `sa ra` (contains a space).
   - Passwords `abc` (too short), `abcdefgh` (no number), `12345678` (no letter).
   - Two different passwords in the confirmation step.
5. Open `data/users.json`: you will see the user with a long `password_hash` and a `salt`, but no plain password.

**Rules:** username 3 to 20 characters (letters, numbers, underscore); password at least 6 characters with a letter and a number.

### FR02: Log in with credentials

1. Choose **Login** and enter `sara` and `coffee1`.
2. **Expected:** "Welcome back, sara!" and the main menu appears.
3. Choose **Logout**, then log in with a wrong password.
4. **Expected:** "Invalid username or password. 2 attempt(s) left." After 3 failed attempts you return to the start menu.

### FR06: Display available beverage categories

1. After logging in, choose **Browse Menu and Order**.
2. **Expected:** the categories Espresso, Milk Coffee, Tea and Cold Drinks.
3. `data/menu.json` is created automatically with this starter menu.
4. Choose **Back** to return to the main menu.

### FR07: Display drinks in a selected category

1. Choose **Browse Menu and Order**, then **Milk Coffee**.
2. **Expected:** Latte ($3.50), Cappuccino ($3.40), Flat White ($3.60) and "Back to categories".
3. Choose **Back to categories** to return to the category list.

### FR15: Customize a beverage in real time

1. Select **Latte**. You are guided through milk type, strength, temperature and syrup.
2. After every choice a live summary shows the drink and the running price.
3. Try this combination: **Oat milk**, **Strong**, **Hot**, **2 pumps of Vanilla**.
4. **Expected final price:** $3.50 + 0.50 (oat) + 0.60 (strong) + 0.80 (vanilla) = **$5.40**.
5. Other checks:
   - Syrup limits are 3 pumps per flavor and 4 pumps in total.
   - Espresso has no milk option, and Black Tea has no milk or strength option.
   - Choose **Change an option** to edit a choice, or **Cancel** to go back.
6. Choose **Confirm drink** to continue to payment.

### FR08: Disable unavailable drinks

1. Close the program. Open `data/inventory.json` in VS Code or any text editor.
2. Change `"milk_ml": 5000` to `"milk_ml": 100` and save the file.
3. Start the program and browse **Milk Coffee**.
4. **Expected:** Latte and Cappuccino show `[UNAVAILABLE]` and cannot be selected. Selecting one explains which ingredient is low.
5. Another check: set `"espresso_shot": 1` and order a Latte with **Strong** strength. After customizing, the app reports that it needs 2 shots and only 1 is left, and offers to change the customization.
6. Restore the original values (`"milk_ml": 5000`, `"espresso_shot": 50`) when finished.

### FR18: Process beverage payments

1. Order a drink and confirm it. The payment menu offers **Card**, **Cash** and **Cancel order**.
2. **Card:** enter `4111 1111 1111 1111`, expiry `12/29`, CVV `123`. **Expected:** "PAYMENT SUCCESSFUL" with a receipt and reference.
3. **Declined card:** use `4111 1111 1111 0000`. **Expected:** "Payment failed: Card declined", and you can retry or choose another method.
4. **Cash:** for a $5.40 drink, enter `10`. **Expected:** change of $4.60. Entering less than the price asks for more.
5. **Cancel order** returns to the menu and nothing is recorded.

### FR19: Record completed transactions and customization parameters

1. Complete a successful payment.
2. **Expected:** "Order O001 recorded."
3. Open `data/orders.json`: the order contains the drink, the full customization, the total price, the payment details (last 4 card digits only) and a timestamp.
4. Open `data/inventory.json`: stock has been reduced by the ingredients used.
5. In the main menu, choose **Order History** to see all your orders, newest first, with a total spent.
6. A cancelled or declined payment must **not** create an order or change stock.

### FR04: Save and name a custom beverage recipe

**Method 1: after an order**
1. After an order is recorded, answer **Yes** to "Save this drink as a recipe?".
2. Enter a name such as `My Morning Latte`.
3. **Expected:** "Recipe 'My Morning Latte' saved (R001)."

**Method 2: without ordering**
1. Choose **My Recipes**, then **Create a new recipe**.
2. Pick a category and drink, customize it, then enter a recipe name.

**Checks:** names must be 3 to 30 characters (letters, numbers, spaces, hyphens, apostrophes). Duplicate names are rejected per user. Typing `c` cancels. Choose **View my recipes** to see the list, and see `data/recipes.json` for the stored data.

### FR05: Modify a saved recipe

1. Choose **My Recipes**, then **Edit a recipe**, and pick a recipe.
2. **Rename:** enter a new name. **Expected:** "Recipe renamed to ..."
3. **Change customization:** the saved choices are pre-selected. Change them and confirm. **Expected:** "Customization saved. New price: ..."
4. Choose **View my recipes** (or reopen the edit screen) to confirm the changes persisted. In `data/recipes.json` the `updated_at` time changes.
5. Cancelling, or confirming without changes, leaves the recipe untouched.

### Bonus: Order from a saved recipe

1. Choose **My Recipes**, then **Order from a recipe**, and pick a recipe.
2. Choose **Order now** to pay, or **Customize for this order only** to adjust just this order (the saved recipe is not changed).
3. The order is recorded and appears in **Order History**.

### Fresh-start test (full run from scratch)

1. Close the program and delete everything inside the `data/` folder.
2. Start the program, register, order a drink, save it as a recipe, edit the recipe, order from it, and check Order History.
3. Close and restart the program, log in, and confirm orders, recipes and stock are still there (data persistence).

---

## 6. Project Structure

```
coffee_app/
├── main.py            # Entry point: start menu, main menu, order flow
├── config.py          # File paths, limits, customization options and prices
├── storage.py         # Safe reading/writing of JSON files
├── utils.py           # Input helpers, ID generation, price formatting
├── session.py         # Holds the logged-in user (in memory only)
├── auth.py            # FR01 Register, FR02 Login
├── menu.py            # FR06 Categories, FR07 Drinks, FR08 Availability
├── customization.py   # FR15 Real-time customization and price calculation
├── payment.py         # FR18 Simulated card and cash payment
├── orders.py          # FR19 Order recording, stock update, order history
├── recipes.py         # FR04 Save, FR05 Edit, order from a recipe
├── README.md          # This document
└── data/              # Created automatically on first run
    ├── users.json
    ├── menu.json
    ├── inventory.json
    ├── orders.json
    └── recipes.json
```

---

## 7. Data Files

All data lives in the `data/` folder as plain JSON text files. You can open them in VS Code or any text editor.

| File | Content |
|---|---|
| `users.json` | Registered users (username, salted password hash) |
| `menu.json` | Categories, drinks, prices and ingredients |
| `inventory.json` | Current stock of each ingredient |
| `orders.json` | Completed orders, payments and customizations |
| `recipes.json` | Saved custom recipes per user |

**To reset the system,** close the program and delete the files in `data/`. They are recreated with starter content on the next run.

**To edit the menu or stock,** close the program, edit `menu.json` or `inventory.json`, save, and start the program again. Keep the JSON format valid (matching quotes, commas and brackets). If a file becomes corrupted, the program saves it as a `.bak` backup and creates a fresh one.

---

## 8. Configuration

Open `config.py` to change:

- Username, password and recipe-name length limits.
- Maximum login attempts (default 3).
- Milk types, strength options, temperatures and syrup flavors, with their price add-ons.
- Maximum syrup pumps and maximum saved recipes per user (default 20).

---

## 9. Troubleshooting

| Problem | Solution |
|---|---|
| `'python' is not recognized` (Windows) | Reinstall Python and tick **Add python.exe to PATH**, or try `py main.py` |
| `python: command not found` (macOS/Linux) | Use `python3 main.py` instead |
| `can't open file 'main.py'` | You are in the wrong folder. Use `cd` to enter the `coffee_app` folder first |
| Password typing shows nothing | This is intentional. Type your password and press `Enter` |
| Password prompt behaves strangely | Run the program from a real terminal (VS Code's integrated terminal works), not an IDE "output" panel |
| Warning that a `.json` file was corrupted | A backup (`.bak`) was saved and a fresh file created. Check your manual edit for a missing comma or quote |
| A drink shows `[UNAVAILABLE]` | Stock is too low. Edit `data/inventory.json` to add stock |
| `ModuleNotFoundError` | Make sure you run `python main.py` from inside the `coffee_app` folder and that all `.py` files are present |

---

## 10. Known Limitations

- Designed for **one user at a time**. Running two copies at once can overwrite each other's data.
- There is **no admin menu**. Restocking and menu changes are made by editing the JSON files.
- Recipes and orders **cannot be deleted** inside the application.
- Payment is **simulated only**. Do not enter real card details.
- Testing is manual (see section 5). There are no automated tests.
