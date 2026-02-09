import streamlit as st
from dataclasses import dataclass, asdict
from typing import Optional
import json

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="LedgerOne",
    layout="centered"
)

# =====================================================
# CORE TAX DATA MODELS (SOURCE OF TRUTH)
# =====================================================

@dataclass
class TaxpayerInfo:
    first_name: str
    last_name: str
    country_of_residence: str
    filing_status: str


@dataclass
class Income1040NR:
    wages_us: float = 0.0
    business_income_eci: float = 0.0
    capital_gains_us: float = 0.0
    fdap_income_us: float = 0.0


@dataclass
class Deductions1040NR:
    state_taxes: float = 0.0
    charitable_contributions: float = 0.0


@dataclass
class Payments1040NR:
    withholding_w2: float = 0.0
    withholding_1042s: float = 0.0
    estimated_payments: float = 0.0


@dataclass
class TaxReturn1040NR:
    taxpayer: TaxpayerInfo
    income: Income1040NR
    deductions: Deductions1040NR
    payments: Payments1040NR

    def total_eci_income(self) -> float:
        return self.income.wages_us + self.income.business_income_eci

    def total_fdap_income(self) -> float:
        return self.income.fdap_income_us

    def adjusted_gross_income(self) -> float:
        return self.total_eci_income() + self.income.capital_gains_us

# =====================================================
# UI
# =====================================================

st.title("LedgerOne — 1040-NR Prototype")
st.caption("Corporate-grade accounting logic · Individual tax interface")

# -----------------------------
# SECTION 1 — TAXPAYER INFO
# -----------------------------

st.header("1. Taxpayer Information")

col1, col2 = st.columns(2)

first_name = col1.text_input("First name")
last_name = col2.text_input("Last name")

country = st.text_input("Country of residence")
filing_status = st.selectbox(
    "Filing status",
    ["Single", "Married Filing Separately", "Other"]
)

taxpayer = TaxpayerInfo(
    first_name=first_name,
    last_name=last_name,
    country_of_residence=country,
    filing_status=filing_status
)

# -----------------------------
# SECTION 2 — INCOME
# -----------------------------

st.header("2. Income (1040-NR)")

st.subheader("Effectively Connected Income (ECI)")

wages_us = st.number_input(
    "US W-2 Wages (Line 1a)",
    min_value=0.0,
    step=100.0
)

business_income = st.number_input(
    "Schedule C Net Income (ECI)",
    min_value=0.0,
    step=100.0
)

st.subheader("Other US Income")

capital_gains = st.number_input(
    "US Capital Gains",
    min_value=0.0,
    step=100.0
)

fdap_income = st.number_input(
    "US FDAP Income (Dividends, Interest)",
    min_value=0.0,
    step=100.0
)

income = Income1040NR(
    wages_us=wages_us,
    business_income_eci=business_income,
    capital_gains_us=capital_gains,
    fdap_income_us=fdap_income
)

# -----------------------------
# SECTION 3 — DEDUCTIONS
# -----------------------------

st.header("3. Deductions (Limited for 1040-NR)")

state_taxes = st.number_input(
    "State & Local Taxes Paid",
    min_value=0.0,
    step=100.0
)

charity = st.number_input(
    "Charitable Contributions",
    min_value=0.0,
    step=100.0
)

deductions = Deductions1040NR(
    state_taxes=state_taxes,
    charitable_contributions=charity
)

# -----------------------------
# SECTION 4 — PAYMENTS
# -----------------------------

st.header("4. Payments & Withholding")

withholding_w2 = st.number_input(
    "W-2 Federal Withholding",
    min_value=0.0,
    step=100.0
)

withholding_1042s = st.number_input(
    "1042-S Withholding",
    min_value=0.0,
    step=100.0
)

estimated = st.number_input(
    "Estimated Tax Payments",
    min_value=0.0,
    step=100.0
)

payments = Payments1040NR(
    withholding_w2=withholding_w2,
    withholding_1042s=withholding_1042s,
    estimated_payments=estimated
)

# -----------------------------
# BUILD RETURN OBJECT
# -----------------------------

tax_return = TaxReturn1040NR(
    taxpayer=taxpayer,
    income=income,
    deductions=deductions,
    payments=payments
)

# -----------------------------
# SECTION 5 — REVIEW
# -----------------------------

st.header("5. Review Summary")

st.metric("Total ECI Income", f"${tax_return.total_eci_income():,.2f}")
st.metric("Total FDAP Income", f"${tax_return.total_fdap_income():,.2f}")
st.metric("Adjusted Gross Income (AGI)", f"${tax_return.adjusted_gross_income():,.2f}")

# -----------------------------
# SECTION 6 — DOWNLOAD
# -----------------------------

st.header("6. Download Draft Return")

return_json = json.dumps(asdict(tax_return), indent=2)

st.download_button(
    label="Download 1040-NR Draft (JSON)",
    data=return_json,
    file_name="1040NR_draft.json",
    mime="application/json"
)

st.caption(
    "This file represents the structured source-of-truth for your return. "
    "PDF generation and e-file can be layered on later."
)
