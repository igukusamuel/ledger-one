import streamlit as st
from dataclasses import dataclass
from typing import List

# =====================================================
# CORE LEDGER (CORPORATE-GRADE, PERSONA-AGNOSTIC)
# =====================================================

@dataclass
class Account:
    name: str
    type: str                     # Asset, Income, Expense
    tax_line: str | None = None
    source: str | None = None     # US / FOREIGN
    character: str | None = None  # ECI / FDAP
    balance: float = 0.0

    def post(self, amount: float):
        self.balance += amount


@dataclass
class JournalLine:
    account: Account
    amount: float


class JournalEntry:
    def __init__(self, memo: str):
        self.memo = memo
        self.lines: List[JournalLine] = []

    def add(self, account: Account, amount: float):
        self.lines.append(JournalLine(account, amount))

    def post(self):
        if round(sum(l.amount for l in self.lines), 2) != 0:
            raise ValueError("Unbalanced journal entry")
        for line in self.lines:
            line.account.post(line.amount)

# =====================================================
# TAX ENGINE (1040 vs 1040-NR)
# =====================================================

def include_income(account: Account, tax_form: str) -> bool:
    if tax_form == "1040":
        return True
    if tax_form == "1040-NR":
        return account.source == "US"
    return False


def generate_schedule_c(accounts, tax_form):
    result = {}
    for acc in accounts:
        if not acc.tax_line:
            continue

        if not include_income(acc, tax_form):
            continue

        if tax_form == "1040-NR" and acc.character != "ECI":
            continue

        result.setdefault(acc.tax_line, 0)
        result[acc.tax_line] += acc.balance

    return result


# =====================================================
# SAMPLE DATA (SIMULATES REAL TRANSACTIONS)
# =====================================================

def load_sample_data(accounts):
    cash = accounts["Cash"]
    revenue = accounts["Consulting Revenue"]
    ads = accounts["Advertising Expense"]
    foreign_div = accounts["Foreign Dividend"]

    # Client payment (US ECI)
    je1 = JournalEntry("Client payment")
    je1.add(cash, 5000)
    je1.add(revenue, -5000)
    je1.post()

    # Advertising expense
    je2 = JournalEntry("Google Ads")
    je2.add(ads, 300)
    je2.add(cash, -300)
    je2.post()

    # Foreign dividend (FDAP)
    je3 = JournalEntry("Foreign dividend")
    je3.add(foreign_div, -450)
    je3.add(cash, 450)
    je3.post()


# =====================================================
# STREAMLIT UI
# =====================================================

st.set_page_config(page_title="LedgerOne Prototype", layout="centered")

st.title("LedgerOne — Personal / Freelancer Prototype")

# -----------------------------
# ONBOARDING (PERSONA + TAX)
# -----------------------------
st.sidebar.header("Setup")

persona = st.sidebar.selectbox(
    "Persona",
    ["Personal", "Freelancer"]
)

tax_form = st.sidebar.selectbox(
    "Tax Filing",
    ["1040", "1040-NR"]
)

st.sidebar.caption("Same ledger • different tax view")

# -----------------------------
# CHART OF ACCOUNTS (TEMPLATE)
# -----------------------------
accounts = {
    "Cash": Account("Cash", "Asset"),

    "Consulting Revenue": Account(
        "Consulting Revenue",
        "Income",
        tax_line="Schedule C – Line 1 (Gross receipts)",
        source="US",
        character="ECI"
    ),

    "Advertising Expense": Account(
        "Advertising Expense",
        "Expense",
        tax_line="Schedule C – Line 18 (Advertising)",
        source="US",
        character="ECI"
    ),

    "Foreign Dividend": Account(
        "Foreign Dividend",
        "Income",
        tax_line="Schedule B – Interest & Dividends",
        source="FOREIGN",
        character="FDAP"
    )
}

load_sample_data(accounts)

# -----------------------------
# DASHBOARD
# -----------------------------
st.subheader("Dashboard")

income = sum(
    a.balance for a in accounts.values()
    if a.type == "Income" and include_income(a, tax_form)
)

expenses = sum(
    a.balance for a in accounts.values()
    if a.type == "Expense"
)

col1, col2, col3 = st.columns(3)
col1.metric("Included Income", f"${abs(income):,.0f}")
col2.metric("Expenses", f"${expenses:,.0f}")
col3.metric("Net", f"${abs(income) - expenses:,.0f}")

# -----------------------------
# SCHEDULE C (FREELANCER ONLY)
# -----------------------------
if persona == "Freelancer":
    st.subheader("Schedule C (Draft)")

    schedule_c = generate_schedule_c(accounts.values(), tax_form)

    if not schedule_c:
        st.info("No Schedule C income included under current tax profile.")
    else:
        for line, amt in schedule_c.items():
            st.write(f"**{line}**: ${abs(amt):,.0f}")

# -----------------------------
# ACCOUNT BALANCES (AUDIT VIEW)
# -----------------------------
st.subheader("Account Balances (Ledger View)")

for acc in accounts.values():
    st.write(
        f"{acc.name} — {acc.type}: "
        f"${acc.balance:,.2f} "
        f"({acc.source or '—'})"
    )

# -----------------------------
# EDUCATIONAL FOOTER
# -----------------------------
st.caption(
    "One ledger • Corporate-grade accounting • "
    "1040 vs 1040-NR handled via tax rules, not separate systems."
)
