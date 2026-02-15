from datetime import datetime
from core.journals import JournalEntry


def generate_accrual_journal(trade, start_date, end_date, auto_reverse=False):

    # Simple day-count accrual (Actual/365)

    days = (end_date - start_date).days
    annual_coupon = trade["face_value"] * trade["coupon_rate"] / 100
    daily_coupon = annual_coupon / 365

    accrued_amount = round(daily_coupon * days, 2)

    journal = JournalEntry(
        entry_date=str(end_date),
        debit_account="Interest Receivable",
        credit_account="Interest Income",
        amount=accrued_amount,
        description=f"Accrual for trade {trade['trade_id']}"
    )

    return journal
