from core.journals import JournalEntry


def record_sale(entity_id, sale_amount, cost_amount):

    journals = []

    # 1️⃣ Record Revenue
    journals.append(
        JournalEntry(
            entity_id,
            None,
            "100000001",      # Cash
            "400000002",      # Cafe Sales Revenue
            sale_amount,
            "Cafe Sale"
        )
    )

    # 2️⃣ Record COGS
    journals.append(
        JournalEntry(
            entity_id,
            None,
            "500000002",      # COGS
            "100000010",      # Inventory
            cost_amount,
            "COGS Recognition"
        )
    )

    return journals
