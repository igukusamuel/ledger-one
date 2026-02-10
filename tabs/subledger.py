import streamlit as st
import pandas as pd
from core.models import JournalEntry

def render():
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
        st.dataframe(
            pd.DataFrame([j.__dict__ for j in st.session_state.journal_entries])
        )
