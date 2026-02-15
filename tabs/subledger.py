import streamlit as st
import pandas as pd
from datetime import date

from core.journals import JournalEntry
from core.accruals import generate_accrual_journal
from core.batch import batch_accruals
from core.gl import generate_trial_balance, post_to_gl
from core.persistence import load_journals, save_journals
from core.audit import log_action, load_audit_log
from core.chart_of_accounts import get_accounts
from core.entities import get_entities
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
    # LOAD ENTITIES + COA
    # ==================================================

    entities = get_entities()
    entity_map = {f"{e[1]} - {e[2]}": e[0] for e in entities}

    accounts_df = get_accounts()
    account_codes = accounts_df["account_code"].tolist()

    # ==================================================
    # 1️⃣ MANUAL ENTRY
    # ==================================================
    with tabs[0]:

        st.subheader("Manual Journal Entry")

        selected_entity = st.selectbox(
            "Select Entity",
            list(entity_map.keys()),
            key="entity_select"
        )

        entity_id = entity_map[selected_entity]

        entry_date = st.date_input("Entry Date", value=date.today(), key="manual_date")

        debit = st.selectbox(
            "Debit Account",
            account_codes,
            key="manual_debit"
        )

        credit = st.selectbox(
            "Credit Account",
            account_codes,
            key="manual_credit"
        )

        amount = st.number_input("Amount", min_value=0.0, key="manual_amount")

        if st.button("Post Entry", key="manual_post"):

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
    # 2️⃣ ACCRUAL GENERATOR
    # ==================================================
    with tabs[1]:

        st.subheader("Single Accrual")

        if not st.session_state.get("trades"):
            st.info("No trades available.")
        else:

            selected_entity = st.selectbox(
                "Entity",
                list(entity_map.keys()),
                key="accrual_entity"
            )

            entity_id = entity_map[selected_entity]

            trade_ids = [t["trade_id"] for t in st.session_state.trades]

            selected_trade = st.selectbox(
    "Select Trade",
    trade_options,
    key="subledger_trade_select"
)

