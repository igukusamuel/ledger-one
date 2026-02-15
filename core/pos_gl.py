from core.journals import JournalEntry
from core.persistence import load_journals, save_journals


def post_sale_to_gl(entity_id, total, tax, revenue, cogs, payment_type):

    journals = load_journals(JournalEntry)

    cash_account = "100000001"
    revenue_account = "400000001"
    tax_account = "200000001"
    inventory_account = "100000002"
    cogs_account = "500000001"

    # 1️⃣ Cash / Card
    journals.append(
        JournalEntry(entity_id, "POS", cash_account, revenue_account, revenue, "POS Sale")
    )

    # 2️⃣ Tax
    journals.append(
        JournalEntry(entity_id, "POS", cash_account, tax_account, tax, "Sales Tax")
    )

    # 3️⃣ COGS
    journals.append(
        JournalEntry(entity_id, "POS", cogs_account, inventory_account, cogs, "COGS")
    )

    save_journals(journals)
