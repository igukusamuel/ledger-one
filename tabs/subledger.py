import streamlit as st
import pandas as pd
from datetime import date

from core.journals import JournalEntry
from core.accruals import generate_accrual_journal
from core.batch import batch_accruals
from core.gl import generate_trial_balance
from core.persistence import load_journals, save_journals
from core.audit import log_action, load_audit_log
from core.chart_of_accounts import get_accounts
from core.entities import get_entities, save_entity
from core.periods import get_closed_through, close_through


# ---------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------

def init_subledger():
    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = load_journals(JournalEntry)


# ---------------------------------------------------
# MAIN RENDER
# ---------------------------------------------------

def render():

    init_subledger()

    st.header("Subledger")

    # ==================================================
    # ENTITY SETUP
    # ==================================================

    st.subheader("Entity Selection")

    entities = get_entities()

    if not entities:

        st.warning("No entities found. Please create one.")

        new_entity_id = st.text_input("Entity ID")
        new_entity_code = st.text_input("Entity Code")
        new_entity_name = st.text_input("Entity Name")

        if st.button("Create Entity"):
            save_entity(new_entity_id, new_entity_code, new_entity_name)
            st.success("Entity Created. Refresh page.")
            st.stop()

        st.stop()

    entity_map = {e[2]: e[0] for e in entities}

    selected_entity = st.selectbox(
        "Select Entity",
        list(entity_map.keys()),
        key="entity_selector"
    )

    entity_id = entity_map[selected_entity]

    accounts_df = get_accounts()
    account_codes = accounts_df["account_code"].tolist() if not accounts_df.empty else []

    tabs = st.tabs([
        "Manual Entry",
        "Accrual Generator",
        "Batch Accruals",
        "Trial Balance",
        "Audit Log",
        "Chart of Accounts",
        "Period Control"
    ])

    # ==================================================
    # 1️⃣ MANUAL ENTRY
    # ==================================================
    with tabs[0]:

        st.subheader("Manual Journal Entry")

        entry_date = st.date_input("Entry Date", value=date.today())

        debit = st.selectbox("Debit Account", account_codes)
        credit = st.selectbox("Credit Account", account_codes)

        amount = st.number_input("Amount", min_value=0.0)

        if st.button("Post Entry"):

            closed_through = get_closed_through()

            if closed_through and entry_date <= closed_through:
                st.error(f"Period closed through {closed_through}. Posting blocked.")
            else:

                journal = JournalEntry(
                    entity_id,
                    str(entry_date),
                    debit,
                    credit,
                    amount,
                    "Manual Entry"
                )

                st.session_state.journal_entries.append(journal)
                save_journals(st.session_state.journal_entries)

                log_action("Manual Entry", f"{entity_id} {debit}/{credit} {amount}")

                st.success("Manual journal posted.")

    # ==================================================
    # 2️⃣ TRIAL BALANCE
    # ==================================================
    with tabs[3]:

        st.subheader("Trial Balance")

        entity_journals = [
            j for j in st.session_state.journal_entries
            if j.entity_id == entity_id
        ]

        tb = generate_trial_balance(entity_journals)
        df = pd.DataFrame(tb)

        if not df.empty:
            st.dataframe(df)

            st.download_button(
                label="Download Trial Balance (CSV)",
                data=df.to_csv(index=False),
                file_name=f"trial_balance_{entity_id}.csv",
                mime="text/csv"
            )
        else:
            st.info("No journal data available.")

    # ==================================================
    # 3️⃣ AUDIT LOG
    # ==================================================
    with tabs[4]:

        st.subheader("Audit Log")

        logs = load_audit_log()

        if logs:
            df = pd.DataFrame(logs, columns=["Timestamp", "Action", "Details"])
            st.dataframe(df)
        else:
            st.info("No audit activity yet.")

    # ==================================================
    # 4️⃣ CHART OF ACCOUNTS
    # ==================================================
    with tabs[5]:

        st.subheader("Chart of Accounts")

        st.dataframe(accounts_df)

        if not accounts_df.empty:
            st.download_button(
                label="Download COA (CSV)",
                data=accounts_df.to_csv(index=False),
                file_name="chart_of_accounts.csv",
                mime="text/csv"
            )

    # ==================================================
    # 5️⃣ PERIOD CONTROL
    # ==================================================
    with tabs[6]:

        st.subheader("Accounting Period Control")

        closed_through = get_closed_through()

        if closed_through:
            st.info(f"Closed through: {closed_through}")
        else:
            st.info("No periods closed.")

        close_date = st.date_input("Close Through Date")

        if st.button("Close Period Through Date"):
            close_through(close_date)
            log_action("Period Closed", f"Closed through {close_date}")
            st.success(f"Period closed through {close_date}")
