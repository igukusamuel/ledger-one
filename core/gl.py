from collections import defaultdict
from core.chart_of_accounts import get_account_type


# ---------------------------------------------------------
# POST TO GL (Aggregate Balances)
# ---------------------------------------------------------

def post_to_gl(journal_entries):
    """
    Returns GL balances by account,
    respecting accounting normal balances.
    """

    ledger = defaultdict(lambda: {
        "Debit": 0.0,
        "Credit": 0.0
    })

    for j in journal_entries:
        ledger[j.debit_account]["Debit"] += j.amount
        ledger[j.credit_account]["Credit"] += j.amount

    balances = {}

    for account, amounts in ledger.items():

        account_type = get_account_type(account)

        debit = amounts["Debit"]
        credit = amounts["Credit"]

        if account_type in ["Asset", "Expense"]:
            balance = debit - credit
        else:
            balance = credit - debit

        balances[account] = round(balance, 2)

    return balances

# =========================================================
# FINANCIAL STATEMENTS ENGINE
# =========================================================

def generate_trial_balance(journal_entries):
    """
    Returns trial balance lines grouped by account.
    Output format:
    [
        {
            "Account": str,
            "Type": str,
            "Debit": float,
            "Credit": float,
            "Balance": float
        }
    ]
    """

    tb = defaultdict(lambda: {
        "Debit": 0.0,
        "Credit": 0.0
    })

    for j in journal_entries:
        tb[j.debit_account]["Debit"] += j.amount
        tb[j.credit_account]["Credit"] += j.amount

    results = []

    for account, amounts in tb.items():

        account_type = get_account_type(account)

        debit = amounts["Debit"]
        credit = amounts["Credit"]

        # Normal balance logic
        if account_type in ["Asset", "Expense"]:
            balance = debit - credit
        else:
            balance = credit - debit

        results.append({
            "Account": account,
            "Type": account_type,
            "Debit": round(debit, 2),
            "Credit": round(credit, 2),
            "Balance": round(balance, 2)
        })

    return sorted(results, key=lambda x: x["Account"])
