import streamlit as st
from dataclasses import dataclass, asdict
import json

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="LedgerOne",
    layout="centered"
)

# =====================================================
# DATA MODELS (CANONICAL SOURCE OF TRUTH)
# =====================================================

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

    def agi(self) -> float:
        return (
            self.income.wages
            + self.income.interest
            + self.income.dividends
            + self.income.capital_gains
        )


@dataclass
class TaxReturn1040NR:
    taxpayer: TaxpayerInfo
    income: Income1040NR
    payments: Payments

    def eci_income(self) -> float:
        return self.income.wages_us + self.income.business_income_eci

    def agi(self) -> float:
        return self.eci_income() + self.income.capital_gains_us


# =====================================================
# SIDEBAR — FORM SELECTION
# =====================================================

st.sidebar.header("Return Type")

return_type = st.sidebar.selectbox(
    "Select Tax Form",
    ["1040 (Resident)", "1040-NR (Nonresident)"]
)

st.sidebar.divider()
st.sidebar.caption("One system • Different tax views")

# =====================================================
# HEADER
# =====================================================

st.title("LedgerOne — Individual Tax Prototype")
st.caption("Corporate-grade architecture · Personal & Nonresident tax")

# =====================================================
# TAXPAYER INFO
# =====================================================

st.header("1. Taxpayer Information")

c1, c2 = st.columns(2)

first_name = c1.text_input("First Name")
last_name = c2.text_input("Last Name")

country = st.text_input("Country of Residence")
filing_status = st.selectbox(
    "Filing Status",
    ["Single", "Married Filing Jointly", "Married Filing Separately", "Other"]
)

taxpayer = TaxpayerInfo(
    first_name=first_name,
    last_name=last_name,
    country_of_residence=country,
    filing_status=filing_status
)

# =====================================================
# INCOME SECTION (DYNAMIC)
# =====================================================

st.header("2. Income")

if return_type == "1040 (Resident)":
    wages = st.number_input("Wages (W-2)", min_value=0.0, step=100.0)
    interest = st.number_input("Interest Income", min_value=0.0, step=50.0)
    dividends = st.number_input("Dividend Income", min_value=0.0, step=50.0)
    cap_gains = st.number_input("Capital Gains", min_value=0.0, step=100.0)

    income = Income1040(
        wages=wages,
        interest=interest,
        dividends=dividends,
        capital_gains=cap_gains
    )

else:
    wages_us = st.number_input("US W-2 Wages (ECI)", min_value=0.0, step=100.0)
    business_eci = st.number_input("Schedule C Net Income (ECI)", min_value=0.0, step=100.0)
    cap_gains_us = st.number_input("US Capital Gains", min_value=0.0, step=100.0)
    fdap = st.number_input("US FDAP Income", min_value=0.0, step=100.0)

    income = Income1040NR(
        wages_us=wages_us,
        business_income_eci=business_eci,
        capital_gains_us=cap_gains_us,
        fdap_income_us=fdap
    )

# =====================================================
# PAYMENTS
# =====================================================

st.header("3. Payments")

withholding = st.number_input("Federal Withholding", min_value=0.0, step=100.0)
estimated = st.number_input("Estimated Payments", min_value=0.0, step=100.0)

payments = Payments(
    withholding=withholding,
    estimated_payments=estimated
)

# =====================================================
# BUILD RETURN
# =====================================================

if return_type == "1040 (Resident)":
    tax_return = TaxReturn1040(
        taxpayer=taxpayer,
        income=income,
        payments=payments
    )
    agi = tax_return.agi()
else:
    tax_return = TaxReturn1040NR(
        taxpayer=taxpayer,
        income=income,
        payments=payments
    )
    agi = tax_return.agi()

# =====================================================
# REVIEW
# =====================================================

st.header("4. Review")

st.metric("Adjusted Gross Income (AGI)", f"${agi:,.2f}")

# =====================================================
# DOWNLOADS
# =====================================================

st.header("5. Download")

user_return_json = json.dumps(asdict(tax_return), indent=2)

st.download_button(
    "Download Your Draft Return (JSON)",
    data=user_return_json,
    file_name="tax_return_draft.json",
    mime="application/json"
)

# -----------------------------
# SAMPLE RETURNS
# -----------------------------

sample_1040 = {
    "taxpayer": {
        "first_name": "John",
        "last_name": "Doe",
        "country_of_residence": "United States",
        "filing_status": "Single"
    },
    "income": {
        "wages": 85000,
        "interest": 500,
        "dividends": 1200,
        "capital_gains": 4000
    },
    "payments": {
        "withholding": 14000,
        "estimated_payments": 0
    }
}

sample_1040nr = {
    "taxpayer": {
        "first_name": "Jane",
        "last_name": "Smith",
        "country_of_residence": "United Kingdom",
        "filing_status": "Single"
    },
    "income": {
        "wages_us": 42000,
        "business_income_eci": 18000,
        "capital_gains_us": 3000,
        "fdap_income_us": 2500
    },
    "payments": {
        "withholding": 9000,
        "estimated_payments": 0
    }
}

st.download_button(
    "Download Sample 1040 (Filled)",
    data=json.dumps(sample_1040, indent=2),
    file_name="sample_1040.json",
    mime="application/json"
)

st.download_button(
    "Download Sample 1040-NR (Filled)",
    data=json.dumps(sample_1040nr, indent=2),
    file_name="sample_1040nr.json",
    mime="application/json"
)

st.caption(
    "These JSON files are the system source-of-truth. "
    "PDF rendering and IRS e-file can be layered on without redesign."
)
