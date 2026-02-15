import streamlit as st
import pandas as pd

from core.gl import generate_financial_statements
from core.persistence import load_journals
from core.journals import JournalEntry
from core.entities import get_entities


def render():

    st.header("General Ledger")

    journals = load_journals(JournalEntry)

    entities = get_entities()
    entity_map = {f"{e[1]} - {e[2]}": e[0] for e in entities}

    selected_entity = st.selectbox(
        "Select Entity",
        list(entity_map.keys()),
        key="gl_entity"
    )

    entity_id = entity_map[selected_entity]

    income_statement, balance_sheet = generate_financial_statements(
        journals,
        entity_id
    )

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
                file_name=f"income_statement_{entity_id}.csv",
                key="is_download"
            )
        else:
            st.info("No income statement data.")

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
                file_name=f"balance_sheet_{entity_id}.csv",
                key="bs_download"
            )
        else:
            st.info("No balance sheet data.")
