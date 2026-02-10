from dataclasses import dataclass
from datetime import date


@dataclass
class JournalEntry:
    date: date
    account: str
    debit: float = 0.0
    credit: float = 0.0
    description: str = ""
    source: str = "SYSTEM"
    trade_id: str | None = None


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
