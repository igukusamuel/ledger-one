from dataclasses import dataclass
from datetime import date

@dataclass
class JournalEntry:
    date: date
    account: str
    debit: float = 0.0
    credit: float = 0.0
    description: str = ""
