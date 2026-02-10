import streamlit as st
import pandas as pd
from dataclasses import dataclass, asdict
from datetime import date
import json
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
    direction: str


@dataclass
class JournalEntry:
    account: str
    debit: float
    credit: float
    memo: str


@dataclass
class TaxpayerInfo:
    first_name: str
    last_name: str
    country_of_residence: str
    filing_status: str


@dataclass
class Income1040:
    wages: float = 0.0
    interest: float = 0.0
    dividends: float = 0.0
    capital_gains: float = 0.0


@dataclass
class Income1040NR:
    wages_us: float = 0.0
    business_income_eci: float = 0.0
    capital_gains_us: float = 0.0
    fdap_income_us: float = 0.0


@dataclass
class Payments:
    withholding: float = 0.0
    estimated_payments: float = 0.0


@dataclass
class TaxReturn1040:
    taxpayer: TaxpayerInfo
    income: Income1040
    payments: Payments

    def agi(self):
        return sum(asdict(self.income).values())


@dataclass
class TaxReturn1040NR:
    taxpayer: TaxpayerInfo
    income: Income1040NR
    payments: Payments

    def agi(self):
        return (
            self.income.wages_us
            + self.income.business_income_eci
            + self.income.capital_gains_us
        )

# =====================================================
# SESSION STATE
# =====================================================

st.session_state.setdefault("trades", [])
st.session_state.setdefault("journal_entries", [])

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Trade Capture System",
        "📒 Subledger",
        "📊 General Ledger",
        "🧾 Tax (1040 / 1040-NR)",
    ]
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
        st.session_state.trades.append(
            BondTrade(
                trade_id, trade_date, maturity_date,
                face_value, coupon, price, direction
            )
        )
        st.success("Trade captured")

    if st.session_state.trades:
        st.dataframe(pd.DataFrame([t.__dict__ for t in st.session_state.trades]))

# =====================================================
# TAB 2 — SUBLEDGER
# =====================================================

with tab2:
    st.header("Subledger")

    if st.session_state.trades:
        trade = st.session_state.trades[-1]
        coupon_cf = trade.face_value * trade.coupon_rate / 100
        st.subheader("Expected Cashflows")
        st.dataframe(
            pd.DataFrame(
                {
                    "Date": [trade.maturity_date, trade.maturity_date],
                    "Type": ["Coupon", "Principal"],
                    "Amount": [coupon_cf, trade.face_value],
                }
            )
        )

    st.subheader("Manual Journal Entry")
    acc = st.text_input("Account")
    debit = st.number_input("Debit", min_value=0.0)
    credit = st.number_input("Credit", min_value=0.0)
    memo = st.text_input("Memo")

    if st.button("Post Entry"):
        st.session_state.journal_entries.append(
            JournalEntry(acc, debit, credit, memo)
        )
        st.success("Journal entry posted")

    if st.session_state.journal_entries:
        st.dataframe(pd.DataFrame([j.__dict__ for j in st.session_state.journal_entries]))

# =====================================================
# TAB 3 — GENERAL LEDGER
# =====================================================

with tab3:
    st.header("General Ledger")

    if st.session_state.journal_entries:
        df = pd.DataFrame([j.__dict__ for j in st.session_state.journal_entries])
        tb = (
            df.groupby("account")[["debit", "credit"]]
            .sum()
            .assign(balance=lambda x: x.debit - x.credit)
            .reset_index()
        )

        st.subheader("Trial Balance")
        st.dataframe(tb)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            tb.to_excel(writer, sheet_name="Trial Balance", index=False)

        st.download_button(
            "Download Trial Balance (Excel)",
            output.getvalue(),
            "trial_balance.xlsx",
        )

# =====================================================
# TAB 4 — TAX (1040 / 1040-NR)
# =====================================================

with tab4:
    st.header("Tax Return")

    form = st.selectbox("Select Tax Form", ["1040", "1040-NR"])

    c1, c2 = st.columns(2)
    first = c1.text_input("First Name")
    last = c2.text_input("Last Name")
    country = st.text_input("Country of Residence")
    status = st.selectbox("Filing Status", ["Single", "MFJ", "MFS"])

    taxpayer = TaxpayerInfo(first, last, country, status)

    st.subheader("Income")

    if form == "1040":
        income = Income1040(
            wages=st.number_input("Wages"),
            interest=st.number_input("Interest"),
            dividends=st.number_input("Dividends"),
            capital_gains=st.number_input("Capital Gains"),
        )
        tax_return = TaxReturn1040(taxpayer, income, Payments())
    else:
        income = Income1040NR(
            wages_us=st.number_input("US Wages (ECI)"),
            business_income_eci=st.number_input("Business Income (ECI)"),
            capital_gains_us=st.number_input("US Capital Gains"),
            fdap_income_us=st.number_input("US FDAP Income"),
        )
        tax_return = TaxReturn1040NR(taxpayer, income, Payments())

    st.metric("Adjusted Gross Income", f"${tax_return.agi():,.2f}")

    st.download_button(
        "Download Draft Return (JSON)",
        json.dumps(asdict(tax_return), indent=2),
        file_name=f"{form}_draft.json",
        mime="application/json",
    )

    st.caption(
        "Tax is layered on top of accounting outputs. "
        "PDF rendering and e-file can be added without redesign."
    )
