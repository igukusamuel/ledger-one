from collections import defaultdict
from core.chart_of_accounts import get_account_type


# =====================================================
# POST TO GL (ACCOUNTING-CORRECT)
# =====================================================

def post_to_gl(journal_entries, entity_id=None):
    """
    Aggregates journal entries into GL balances.
    Respects normal balance by account type.
    Optional entity filter.
    """

    ledger = defaultdict(lambda: {
        "Debit": 0.0,
        "Credit": 0.0
    })

    for j in journal_entries:

        if entity_id and j.entity_id != entity_id:
            continue

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


# =====================================================
# TRIAL BALANCE
# =====================================================

def generate_trial_balance(journal_entries, entity_id=None):

    ledger = defaultdict(lambda: {
        "Debit": 0.0,
        "Credit": 0.0
    })

    for j in journal_entries:

        if entity_id and j.entity_id != entity_id:
            continue

        ledger[j.debit_account]["Debit"] += j.amount
        ledger[j.credit_account]["Credit"] += j.amount

    trial_balance = []

    for account, amounts in ledger.items():

        trial_balance.append({
            "Account": account,
            "Debit": round(amounts["Debit"], 2),
            "Credit": round(amounts["Credit"], 2)
        })

    return trial_balance


# =====================================================
# FINANCIAL STATEMENTS
# =====================================================

def generate_financial_statements(journal_entries, entity_id=None):
    """
    Returns:
        income_statement (dict)
        balance_sheet (dict)
    """

    gl = post_to_gl(journal_entries, entity_id)

    income_statement = {}
    balance_sheet = {}

    for account, balance in gl.items():

        account_type = get_account_type(account)

        if account_type in ["Revenue", "Expense"]:
            income_statement[account] = balance

        elif account_type in ["Asset", "Liability", "Equity"]:
            balance_sheet[account] = balance

    return income_statement, balance_sheet
