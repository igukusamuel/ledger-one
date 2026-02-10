import streamlit as st
from core.state import init_state
from tabs import trade_capture, subledger, general_ledger, tax

st.set_page_config(page_title="LedgerOne", layout="wide")
init_state()

st.title("LedgerOne")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Trade Capture",
        "📒 Subledger",
        "📊 General Ledger",
        "🧾 Tax",
    ]
)

with tab1:
    trade_capture.render()

with tab2:
    subledger.render()

with tab3:
    general_ledger.render()

with tab4:
    tax.render()
