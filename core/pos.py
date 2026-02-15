from datetime import datetime
from core.journals import JournalEntry
from core.inventory import update_inventory
from core.tax_engine import calculate_sales_tax


def record_sale(entity_id, cart, tax_rate):

    journals = []
    subtotal = 0
    total_cogs = 0

    for item in cart:
        subtotal += item["price"] * item["quantity"]
        cogs = update_inventory(item["sku"], item["quantity"])
        total_cogs += cogs

    tax, total = calculate_sales_tax(subtotal, tax_rate)

    entry_date = str(datetime.today().date())

    # Cash / Revenue
    journals.append(JournalEntry(
        entity_id,
        entry_date,
        "100000001",  # Cash
        "400000002",  # Sales Revenue
        subtotal,
        "Cafe Revenue"
    ))

    # Sales Tax
    journals.append(JournalEntry(
        entity_id,
        entry_date,
        "100000001",
        "200000010",  # Sales Tax Payable
        tax,
        "Sales Tax"
    ))

    # COGS
    journals.append(JournalEntry(
        entity_id,
        entry_date,
        "500000003",  # COGS
        "100000020",  # Inventory
        total_cogs,
        "Cost of Goods Sold"
    ))

    return journals, total
