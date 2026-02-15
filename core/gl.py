from collections import defaultdict

def post_to_gl(journal_entries):

    ledger = defaultdict(float)

    for j in journal_entries:
        ledger[j.debit_account] += j.amount
        ledger[j.credit_account] -= j.amount

    return dict(ledger)


def generate_trial_balance(journal_entries):

    gl = post_to_gl(journal_entries)

    trial_balance = []

    for account, balance in gl.items():
        trial_balance.append({
            "Account": account,
            "Debit": balance if balance > 0 else 0,
            "Credit": abs(balance) if balance < 0 else 0
        })

    return trial_balance


def generate_financial_statements(journal_entries):

    gl = post_to_gl(journal_entries)

    income_statement = {}
    balance_sheet = {}

    for account, balance in gl.items():

        if "Revenue" in account or "Income" in account:
            income_statement[account] = balance

        elif "Expense" in account:
            income_statement[account] = balance

        else:
            balance_sheet[account] = balance

    return income_statement, balance_sheet
