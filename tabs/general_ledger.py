import streamlit as st
import pandas as pd

from core.gl import generate_financial_statements
from core.persistence import load_journals
from core.journals import JournalEntry
from core.entities import get_entities


def render():

    st.header("General Ledger")

    # ---------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------

    journals = load_journals(JournalEntry)
    entities = get_entities()

    if not entities:
        st.warning("No entities available.")
        return

    entity_map = {f"{e[1]} - {e[2]}": e[0] for e in entities}

    selected_entity = st.selectbox(
        "Select Entity",
        list(entity_map.keys()),
        key="gl_entity"
    )

    entity_id = entity_map[selected_entity]

    # Filter journals by entity
    entity_journals = [
        j for j in journals if j.entity_id == entity_id
    ]

    if not entity_journals:
        st.info("No journal entries for selected entity.")
        return

    statements = generate_financial_statements(entity_journals)

    income_data = statements["Income Statement"]
    balance_data = statements["Balance Sheet"]

    tabs = st.tabs(["Income Statement", "Balance Sheet"])

    # =====================================================
    # INCOME STATEMENT
    # =====================================================
    with tabs[0]:

        st.subheader("Income Statement")

        lines = income_data["Lines"]

        if lines:

            df = pd.DataFrame(lines)

            revenue_df = df[df["Type"] == "Revenue"]
            expense_df = df[df["Type"] == "Expense"]

            if not revenue_df.empty:
                st.markdown("### Revenue")
                st.dataframe(revenue_df[["Account", "Balance"]])

            if not expense_df.empty:
                st.markdown("### Expenses")
                st.dataframe(expense_df[["Account", "Balance"]])

            st.markdown("---")
            st.markdown(f"**Total Revenue:** {income_data['Total Revenue']:.2f}")
            st.markdown(f"**Total Expense:** {income_data['Total Expense']:.2f}")
            st.markdown(f"## Net Income: {income_data['Net Income']:.2f}")

            export_df = pd.DataFrame(lines)

            st.download_button(
                "Download Income Statement",
                export_df.to_csv(index=False),
                file_name=f"income_statement_{entity_id}.csv",
                mime="text/csv",
                key="is_download"
            )

        else:
            st.info("No income statement data.")

    # =====================================================
    # BALANCE SHEET
    # =====================================================
    with tabs[1]:

        st.subheader("Balance Sheet")

        if balance_data:

            df = pd.DataFrame(balance_data)

            assets = df[df["Type"] == "Asset"]
            liabilities = df[df["Type"] == "Liability"]
            equity = df[df["Type"] == "Equity"]

            if not assets.empty:
                st.markdown("### Assets")
                st.dataframe(assets[["Account", "Balance"]])

            if not liabilities.empty:
                st.markdown("### Liabilities")
                st.dataframe(liabilities[["Account", "Balance"]])

            if not equity.empty:
                st.markdown("### Equity")
                st.dataframe(equity[["Account", "Balance"]])

            st.markdown("---")

            st.markdown(f"**Total Assets:** {assets['Balance'].sum():.2f}")
            st.markdown(f"**Total Liabilities:** {liabilities['Balance'].sum():.2f}")
            st.markdown(f"**Total Equity:** {equity['Balance'].sum():.2f}")

            st.download_button(
                "Download Balance Sheet",
                df.to_csv(index=False),
                file_name=f"balance_sheet_{entity_id}.csv",
                mime="text/csv",
                key="bs_download"
            )

        else:
            st.info("No balance sheet data.")
