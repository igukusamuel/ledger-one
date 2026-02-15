from dataclasses import dataclass
from datetime import date


@dataclass
class JournalEntry:
    def __init__(self, entity_id, entry_date,
                 debit_account, credit_account,
                 amount, description):

        self.entity_id = entity_id
        self.entry_date = entry_date
        self.debit_account = debit_account
        self.credit_account = credit_account
        self.amount = amount
        self.description = description



def generate_accrual_journal(accrual_date: date, amount: float):
    return [
        JournalEntry(
            date=accrual_date,
            account="Interest Receivable",
            debit=amount,
            description="Interest accrual",
            source="SYSTEM",
        ),
        JournalEntry(
            date=accrual_date,
            account="Interest Income",
            credit=amount,
            description="Interest accrual",
            source="SYSTEM",
        ),
    ]
