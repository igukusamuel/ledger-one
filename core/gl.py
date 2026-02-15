from collections import defaultdict
from core.chart_of_accounts import get_account_type


# ---------------------------------------------------------
# POST TO GL (Aggregate Balances)
# ---------------------------------------------------------

def post_to_gl(journal_entries):

    gl = defaultdict(float)

    for j in journal_entries:

        # Debit increases
        gl[j.debit_account] += j.amount

        # Credit decreases
        gl[j.credit_account] -= j.amount

    return gl


# ---------------------------------------------------------
# GENERATE TRIAL BALANCE
# ---------------------------------------------------------

def generate_trial_balance(journal_entries):

    gl = post_to_gl(journal_entries)

    trial_balance = []

    for account, balance in gl.items():

        account_type = get_account_type(account)

        trial_balance.append({
            "Account": account,
            "Type": account_type,
            "Debit": balance if balance > 0 else 0,
            "Credit": abs(balance) if balance < 0 else 0
        })

    return trial_balance
