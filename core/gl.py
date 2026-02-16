from collections import defaultdict
import pandas as pd


# --------------------------------------------------
# POST JOURNAL ENTRIES TO GL
# --------------------------------------------------

def post_to_gl(journal_entries):
    """
    journal_entries = list of dicts with:
    debit_account, credit_account, amount
    """
    gl = defaultdict(float)

    for j in journal_entries:
        gl[j["debit_account"]] += j["amount"]
        gl[j["credit_account"]] -= j["amount"]

    return gl


# --------------------------------------------------
# GENERATE TRIAL BALANCE
# --------------------------------------------------

def generate_trial_balance(journal_entries):
    """
    Accepts list of journal entry dicts
    Returns pandas DataFrame
    """

    gl = post_to_gl(journal_entries)

    rows = []

    for account, balance in gl.items():
        debit = balance if balance > 0 else 0
        credit = abs(balance) if balance < 0 else 0

        rows.append({
            "Account": account,
            "Debit": round(debit, 2),
            "Credit": round(credit, 2)
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        totals = {
            "Account": "TOTAL",
            "Debit": df["Debit"].sum(),
            "Credit": df["Credit"].sum()
        }
        df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)

    return df


# --------------------------------------------------
# GENERATE FINANCIAL STATEMENTS
# --------------------------------------------------

def generate_financial_statements(journal_entries):

    gl = post_to_gl(journal_entries)

    revenue = 0
    expenses = 0

    for account, balance in gl.items():

        if "Revenue" in account:
            revenue += abs(balance)

        if "COGS" in account or "Expense" in account:
            expenses += abs(balance)

    net_income = revenue - expenses

    income_statement = pd.DataFrame({
        "Line Item": [
            "Revenue",
            "Expenses",
            "Net Income"
        ],
        "Amount": [
            round(revenue, 2),
            round(expenses, 2),
            round(net_income, 2)
        ]
    })

    return income_statement
