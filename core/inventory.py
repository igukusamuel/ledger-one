from core.persistence import load_inventory, save_inventory


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
