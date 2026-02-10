from core.journals import JournalEntry
from datetime import date

def reverse_accrual(accrual_entry, reversal_date: date):
    """
    Creates reversing entry for an accrual journal
    """
    return JournalEntry(
        date=reversal_date,
        account=accrual_entry.account,
        debit=accrual_entry.credit,
        credit=accrual_entry.debit,
        description=f"Reversal of accrual from {accrual_entry.date}",
        source="SYSTEM",
        trade_id=accrual_entry.trade_id
    )
