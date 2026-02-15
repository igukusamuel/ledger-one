from core.persistence import save_journals, load_journals
from core.journals import JournalEntry
from datetime import date

def post_sale_to_gl(entity_id, total, tax, revenue, cogs, payment_type):

    journals = load_journals(JournalEntry)

    today = str(date.today())

    cash_account = "100000001" if payment_type == "Cash" else "100000002"

    entries = [

        # Debit Cash / Card
        JournalEntry(entity_id, today, cash_account, "400000001", revenue),

        # Credit Sales Tax
        JournalEntry(entity_id, today, cash_account, "200000001", tax),

        # COGS
        JournalEntry(entity_id, today, "500000001", "100000003", cogs),
    ]

    journals.extend(entries)

    save_journals(journals)
