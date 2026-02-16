from collections import defaultdict
from datetime import date

from core.chart_of_accounts import get_account_type
from core.persistence import save_journals, load_journals
from core.journals import JournalEntry


# =====================================================
# POST SALE TO GL
# =====================================================

def post_sale_to_gl(entity_id, total, tax, revenue, cogs, payment_type):

    today = str(date.today())
    journals = load_journals(JournalEntry)

    cash_account = "100000001" if payment_type == "Cash" else "100000002"

    entries = [

        # 1️⃣ Record Revenue
        JournalEntry(entity_id, today, cash_account, "400000001", revenue),

        # 2️⃣ Record Sales Tax Liability
        JournalEntry(entity_id, today, cash_account, "200000001", tax),

        # 3️⃣ Record COGS
        JournalEntry(entity_id, today, "500000001", "100000003", cogs),
    ]

    journals.extend(entries)
    save_journals(journals)


# =====================================================
# POST TO GL (AGGREGATE BALANCES)
# =====================================================

def post_to_gl(journal_entries, entity_id=None):

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

        # Respect normal balance
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
