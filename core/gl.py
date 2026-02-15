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

def generate_financial_statements(journal_entries):

    gl = post_to_gl(journal_entries)

    income_statement = []
    balance_sheet = []

    for account, balance in gl.items():

        account_type = get_account_type(account)

        if account_type in ["Revenue", "Expense"]:
            income_statement.append({
                "Account": account,
                "Balance": balance
            })

        elif account_type in ["Asset", "Liability", "Equity"]:
            balance_sheet.append({
                "Account": account,
                "Balance": balance
            })

    return {
        "Income Statement": income_statement,
        "Balance Sheet": balance_sheet
    }
