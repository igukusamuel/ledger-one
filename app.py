import streamlit as st

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    layout="wide",
    page_title="LedgerOne Café Test"
)

st.title("LedgerOne ERP System")
st.write("APP LOADED")

# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

from core.persistence import initialize_db
initialize_db()

st.write("DATABASE INITIALIZED")

# --------------------------------------------------
# IMPORT CAFE MODULE
# --------------------------------------------------

import tabs.cafe as cafe

st.write("CAFE MODULE IMPORTED")

# --------------------------------------------------
# RENDER CAFE
# --------------------------------------------------

cafe.render()

st.write("RENDER COMPLETE")
