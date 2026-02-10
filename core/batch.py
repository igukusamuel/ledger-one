from datetime import timedelta


def batch_accruals(start_date, end_date, accrual_func):
    """
    Generate accrual journals from start_date to end_date (inclusive)
    accrual_func(date) must return a LIST of JournalEntry
    """
    current = start_date
    journals = []

    while current <= end_date:
        journals.extend(accrual_func(current))
        current += timedelta(days=1)

    return journals
