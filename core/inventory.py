import pandas as pd
from core.persistence import load_inventory, save_inventory

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

def update_inventory(sku, quantity_sold):
    inventory = load_inventory()

    if sku not in inventory:
        raise Exception("SKU not found")

    inventory[sku]["quantity"] -= quantity_sold

    if inventory[sku]["quantity"] < 0:
        raise Exception("Negative inventory not allowed")

    save_inventory(inventory)

    return inventory[sku]["unit_cost"] * quantity_sold


def add_inventory_item(sku, name, quantity, unit_cost):
    inventory = load_inventory()

    inventory[sku] = {
        "name": name,
        "quantity": quantity,
        "unit_cost": unit_cost
    }

    save_inventory(inventory)
