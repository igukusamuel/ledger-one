from collections import defaultdict
from core.chart_of_accounts import get_account_type


def post_to_gl(journal_entries, entity_id):

    ledger = defaultdict(float)

    for j in journal_entries:
        if j.entity_id == entity_id:
            ledger[j.debit_account] += j.amount
            ledger[j.credit_account] -= j.amount

    return dict(ledger)


def generate_trial_balance(journal_entries, entity_id):

    gl = post_to_gl(journal_entries, entity_id)

    trial_balance = []

    for account, balance in gl.items():
        trial_balance.append({
            "Account": account,
            "Debit": balance if balance > 0 else 0,
            "Credit": abs(balance) if balance < 0 else 0
        })

    return trial_balance


def generate_financial_statements(journal_entries, entity_id):

    gl = post_to_gl(journal_entries, entity_id)

    income_statement = {}
    balance_sheet = {}

    for account, balance in gl.items():

        acc_type = get_account_type(account)

        if acc_type in ["Revenue", "Expense"]:
            income_statement[account] = balance
        else:
            balance_sheet[account] = balance

    return income_statement, balance_sheet
