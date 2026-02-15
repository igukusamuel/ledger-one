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

    # 1️⃣ Cash + Revenue + Tax
    journals.append(
        JournalEntry(
            entity_id,
            None,
            "100000001",
            "400000002",
            subtotal,
            "Cafe Revenue"
        )
    )

    journals.append(
        JournalEntry(
            entity_id,
            None,
            "100000001",
            "200000010",
            tax,
            "Sales Tax Payable"
        )
    )

    # 2️⃣ COGS
    journals.append(
        JournalEntry(
            entity_id,
            None,
            "500000003",
            "100000020",
            total_cogs,
            "COGS"
        )
    )

    return journals, total
