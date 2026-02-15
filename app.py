import streamlit as st

st.set_page_config(layout="wide")

st.title("LedgerOne ERP System")

st.write("APP LOADED")

import tabs.cafe as cafe

st.write("CAFE IMPORTED")

cafe.render()
