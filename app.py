import streamlit as st
from tabs.trade_capture import render as trade_capture_render
from tabs.subledger import render as subledger_render
from tabs.general_ledger import render as gl_render
from tabs.tax import render as tax_render
from core.persistence import initialize_db
from core.entities import initialize_entity_table, seed_default_entity
from core.chart_of_accounts import initialize_coa, seed_default_accounts

from tabs.cafe import render as cafe_render


initialize_coa()
seed_default_accounts()

initialize_entity_table()
seed_default_entity()

initialize_db()

st.set_page_config(layout="wide")
st.title("LedgerOne")

elif selected_tab == "Cafe Operations":
    cafe_render()


tab1, tab2, tab3, tab4 = st.tabs([
    "Trade Capture",
    "Subledger",
    "General Ledger",
    "Tax (1040 / 1040-NR)"
])

with tab1:
    trade_capture_render()

with tab2:
    subledger_render()

with tab3:
    gl_render()

with tab4:
    tax_render()
