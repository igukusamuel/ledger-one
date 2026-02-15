import streamlit as st

from tabs.trade_capture import render as trade_capture_render
from tabs.subledger import render as subledger_render
from tabs.general_ledger import render as gl_render
from tabs.tax import render as tax_render
from tabs.cafe import render as cafe_render
from tabs.coffee_pos import render as coffee_render
from core.persistence import initialize_db

initialize_db()

st.set_page_config(layout="wide")
st.title("LedgerOne ERP System")

tabs = st.tabs([
    "Trade Capture",
    "Subledger",
    "General Ledger",
    "Tax",
    "Cafe",
    "Coffee POS"
])

with tabs[0]:
    trade_capture_render()

with tabs[1]:
    subledger_render()

with tabs[2]:
    gl_render()

with tabs[3]:
    tax_render()

with tabs[4]:
    cafe_render()

with tabs[5]:
    coffee_render()
