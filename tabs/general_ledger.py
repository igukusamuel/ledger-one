import streamlit as st
import pandas as pd

from core.gl import generate_financial_statements
from core.persistence import load_journals
from core.journals import JournalEntry


def render():

    st.header("General Ledger")

    journals = load_journals(JournalEntry)

    income_statement, balance_sheet = generate_financial_statements(journals)

    tabs = st.tabs(["Income Statement", "Balance Sheet"])

    with tabs[0]:
        if income_statement:
            df = pd.DataFrame(
                list(income_statement.items()),
                columns=["Account", "Amount"]
            )
            st.dataframe(df)

            st.download_button(
                "Download Income Statement",
                df.to_csv(index=False),
                file_name="income_statement.csv"
            )
        else:
            st.info("No data.")

    with tabs[1]:
        if balance_sheet:
            df = pd.DataFrame(
                list(balance_sheet.items()),
                columns=["Account", "Amount"]
            )
            st.dataframe(df)

            st.download_button(
                "Download Balance Sheet",
                df.to_csv(index=False),
                file_name="balance_sheet.csv"
            )
        else:
            st.info("No data.")
