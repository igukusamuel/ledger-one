from core.journals import JournalEntry
from core.persistence import save_journals, load_journals


def post_sale_to_gl(total, tax):

    journals = load_journals(JournalEntry)

    # Debit Cash
    journals.append(
        JournalEntry("CAFE", str("POS"), "100000001", "400000001", total - tax, "POS Sale")
    )

    # Credit Sales Revenue
    journals.append(
        JournalEntry("CAFE", str("POS"), "100000001", "200000001", tax, "Sales Tax Payable")
    )

    save_journals(journals)
