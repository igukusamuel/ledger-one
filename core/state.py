import streamlit as st

def init_state():
    st.session_state.setdefault("trades", [])
    st.session_state.setdefault("journal_entries", [])
