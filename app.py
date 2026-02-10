import streamlit as st
import pandas as pd
from dataclasses import dataclass
from datetime import date
import io

st.set_page_config(page_title="LedgerOne", layout="wide")

# =====================================================
# DATA MODELS
# =====================================================

@dataclass
class BondTrade:
    trade_id: str
    trade_date: date
    maturity_date: date
    face_value: float
    coupon_rate: float
    price: float
    direction: str  # Buy / Sell


@dataclass
class JournalEntry:
    account: str
    debit: float
    credit: float
    memo: str


# =====================================================
# SESSION STATE
# =====================================================

if "trades" not in st.session_state:
    st.session_state.trades = []

if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = []

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3 = st.tabs(
    ["📈 Trade Capture System", "📒 Subledger", "📊 General Ledger"]
)

# =====================================================
# TAB 1 — TRADE CAPTURE
# =====================================================

with tab1:
    st.header("Trade Capture — Plain Vanilla Bond")

    c1, c2 = st.columns(2)

    trade_id = c1.text_input("Trade ID")
    direction = c2.selectbox("Direction", ["Buy", "Sell"])

    trade_date = c1.date_input("Trade Date")
    maturity_date = c2.date_input("Maturity Date")

    face_value = c1.number_input("Face Value", min_value=0.0, step=1000.0)
    coupon = c2.number_input("Coupon Rate (%)", min_value=0.0, step=0.25)

    price = st.number_input("Clean Price (%)", min_value=0.0, step=0.1)

    if st.button("Capture Trade"):
        trade = BondTrade(
            trade_id=trade_id,
            trade_date=trade_date,
            maturity_date=maturity_date,
            face_value=face_value,
            coupon_rate=coupon,
            price=price,
            direction=direction
        )
        st.session_state.trades.append(trade)
        st.success("Trade captured successfully")

    if st.session_state.trades:
        st.subheader("Captured Trades")
        st.dataframe(pd.DataFrame([t.__dict__ for t in st.session_state.trades]))

# =====================================================
# TAB 2 — SUBLEDGER
# =====================================================

with tab2:
    st.header("Subledger — Instrument Accounting")

    if not st.session_state.trades:
        st.info("No trades captured yet.")
    else:
        trade = st.session_state.trades[-1]

        st.subheader(f"Expected Cashflows for Trade {trade.trade_id}")

        coupon_cf = trade.face_value * trade.coupon_rate / 100
        principal_cf = trade.face_value

        cashflows = pd.DataFrame(
            {
                "Date": [trade.maturity_date, trade.maturity_date],
                "Type": ["Coupon", "Principal"],
                "Amount": [coupon_cf, principal_cf],
            }
        )

        st.dataframe(cashflows)

    st.subheader("Manual Journal Entry")

    acc = st.text_input("Account")
    debit = st.number_input("Debit", min_value=0.0, step=100.0)
    credit = st.number_input("Credit", min_value=0.0, step=100.0)
    memo = st.text_input("Memo")

    if st.button("Post Entry"):
        je = JournalEntry(acc, debit, credit, memo)
        st.session_state.journal_entries.append(je)
        st.success("Journal entry posted")

    if st.session_state.journal_entries:
        st.subheader("Posted Journal Entries")
        st.dataframe(pd.DataFrame([j.__dict__ for j in st.session_state.journal_entries]))

# =====================================================
# TAB 3 — GENERAL LEDGER
# =====================================================

with tab3:
    st.header("General Ledger & Financial Statements")

    if not st.session_state.journal_entries:
        st.info("No accounting entries available.")
    else:
        df = pd.DataFrame([j.__dict__ for j in st.session_state.journal_entries])

        tb = (
            df.groupby("account")[["debit", "credit"]]
            .sum()
            .assign(balance=lambda x: x.debit - x.credit)
            .reset_index()
        )

        st.subheader("Trial Balance")
        st.dataframe(tb)

        income_stmt = tb[tb["account"].str.contains("Revenue|Expense", case=False)]
        balance_sheet = tb[~tb.index.isin(income_stmt.index)]

        st.subheader("Income Statement (Mock)")
        st.dataframe(income_stmt)

        st.subheader("Balance Sheet (Mock)")
        st.dataframe(balance_sheet)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            tb.to_excel(writer, sheet_name="Trial Balance", index=False)
            income_stmt.to_excel(writer, sheet_name="Income Statement", index=False)
            balance_sheet.to_excel(writer, sheet_name="Balance Sheet", index=False)

        st.download_button(
            "Download Financial Statements (Excel)",
            data=output.getvalue(),
            file_name="financial_statements.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
