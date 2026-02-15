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


# =========================================================
# FINANCIAL STATEMENTS ENGINE
# =========================================================

def generate_financial_statements(journal_entries):
    """
    Generates:
        - Income Statement
        - Balance Sheet

    Based on posted GL balances.
    """

    gl = post_to_gl(journal_entries)

    income_statement = []
    balance_sheet = []

    total_revenue = 0
    total_expense = 0

    for account, balance in gl.items():

        account_type = get_account_type(account)

        if account_type == "Revenue":
            income_statement.append({
                "Account": account,
                "Type": "Revenue",
                "Balance": balance
            })
            total_revenue += balance

        elif account_type == "Expense":
            income_statement.append({
                "Account": account,
                "Type": "Expense",
                "Balance": balance
            })
            total_expense += balance

        elif account_type in ["Asset", "Liability", "Equity"]:
            balance_sheet.append({
                "Account": account,
                "Type": account_type,
                "Balance": balance
            })

    net_income = total_revenue - total_expense

    # Add Net Income to Equity section of balance sheet
    balance_sheet.append({
        "Account": "Current Period Net Income",
        "Type": "Equity",
        "Balance": net_income
    })

    return {
        "Income Statement": {
            "Lines": income_statement,
            "Total Revenue": total_revenue,
            "Total Expense": total_expense,
            "Net Income": net_income
        },
        "Balance Sheet": balance_sheet
    }
