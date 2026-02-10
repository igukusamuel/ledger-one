import streamlit as st
import pandas as pd
import io

def render():
    st.header("General Ledger")

    if not st.session_state.journal_entries:
        st.info("No journal entries available.")
        return

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
