import streamlit as st
import json
from dataclasses import asdict
from core.models import (
    TaxpayerInfo,
    Income1040,
    Income1040NR,
)

def render():
    st.header("Tax — 1040 / 1040-NR")

    form = st.selectbox("Tax Form", ["1040", "1040-NR"])

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
    else:
        income = Income1040NR(
            wages_us=st.number_input("US Wages (ECI)"),
            business_income_eci=st.number_input("Business Income (ECI)"),
            capital_gains_us=st.number_input("US Capital Gains"),
            fdap_income_us=st.number_input("US FDAP Income"),
        )

    st.download_button(
        "Download Draft Return (JSON)",
        json.dumps(
            {
                "taxpayer": asdict(taxpayer),
                "income": asdict(income),
                "form": form,
            },
            indent=2,
        ),
        file_name=f"{form}_draft.json",
        mime="application/json",
    )
