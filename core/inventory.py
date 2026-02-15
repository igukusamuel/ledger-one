import pandas as pd

# Demo inventory
INVENTORY = pd.DataFrame([
    {"Product": "Espresso", "Price": 3.00, "Stock": 100},
    {"Product": "Latte", "Price": 4.50, "Stock": 100},
    {"Product": "Cappuccino", "Price": 4.00, "Stock": 100},
    {"Product": "Blueberry Muffin", "Price": 2.75, "Stock": 50},
])


def get_inventory():
    return INVENTORY


def update_inventory(product, quantity):
    INVENTORY.loc[INVENTORY["Product"] == product, "Stock"] -= quantity
