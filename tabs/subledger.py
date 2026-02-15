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

from core.entities import get_entities, save_entity

st.subheader("Entity Selection")

entities = get_entities()

if not entities:

    st.warning("No entities found. Please create one.")

    new_entity_id = st.text_input("Entity ID")
    new_entity_code = st.text_input("Entity Code")
    new_entity_name = st.text_input("Entity Name")

    if st.button("Create Entity"):
        save_entity(new_entity_id, new_entity_code, new_entity_name)
        st.success("Entity Created. Please refresh page.")
        st.stop()

    st.stop()

# Build mapping safely
entity_map = {e[2]: e[0] for e in entities}

selected_entity = st.selectbox(
    "Select Entity",
    list(entity_map.keys()),
    key="entity_selector"
)

entity_id = entity_map[selected_entity]


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
                trade_ids,
                key="accrual_trade"
            )

            start = st.date_input("Start Date", key="accrual_start")
            end = st.date_input("End Date", key="accrual_end")

            if st.button("Generate Accrual", key="accrual_btn"):

                closed_through = get_closed_through()

                if closed_through and end <= closed_through:
                    st.error("Cannot accrue into closed period.")
                else:

                    trade = next(
                        t for t in st.session_state.trades
                        if t["trade_id"] == selected_trade
                    )

                    journal = generate_accrual_journal(
                        trade,
                        start,
                        end,
                        entity_id=entity_id
                    )

                    st.session_state.journal_entries.append(journal)
                    save_journals(st.session_state.journal_entries)

                    log_action("Accrual Generated", f"{entity_id} {selected_trade}")

                    st.success("Accrual posted.")

    # ==================================================
    # 3️⃣ BATCH ACCRUALS
    # ==================================================
    with tabs[2]:

        st.subheader("Batch Accrual Engine")

        selected_entity = st.selectbox(
            "Entity",
            list(entity_map.keys()),
            key="batch_entity"
        )

        entity_id = entity_map[selected_entity]

        cutoff = st.date_input("Cutoff Date", value=date.today(), key="batch_cutoff")

        if st.button("Run Batch", key="batch_btn"):

            closed_through = get_closed_through()

            if closed_through and cutoff <= closed_through:
                st.error("Batch date is within closed period.")
            else:

                journals = batch_accruals(
                    st.session_state.get("trades", []),
                    cutoff,
                    entity_id=entity_id
                )

                st.session_state.journal_entries.extend(journals)
                save_journals(st.session_state.journal_entries)

                log_action("Batch Accrual", f"{entity_id} {len(journals)} entries")

                st.success(f"{len(journals)} accruals generated.")

    # ==================================================
    # 4️⃣ TRIAL BALANCE (ENTITY SPECIFIC)
    # ==================================================
    with tabs[3]:

        st.subheader("Trial Balance")

        selected_entity = st.selectbox(
            "Entity",
            list(entity_map.keys()),
            key="tb_entity"
        )

        entity_id = entity_map[selected_entity]

        tb = generate_trial_balance(
            [j for j in st.session_state.journal_entries if j.entity_id == entity_id]
        )

        df = pd.DataFrame(tb)

        if not df.empty:

            st.dataframe(df)

            st.download_button(
                label="Download Trial Balance (CSV)",
                data=df.to_csv(index=False),
                file_name=f"trial_balance_{entity_id}.csv",
                mime="text/csv",
                key="tb_download"
            )
        else:
            st.info("No journal data available.")

    # ==================================================
    # 5️⃣ AUDIT LOG
    # ==================================================
    with tabs[4]:

        st.subheader("Audit Log")

        logs = load_audit_log()

        if logs:
            df = pd.DataFrame(
                logs,
                columns=["Timestamp", "Action", "Details"]
            )
            st.dataframe(df)
        else:
            st.info("No audit activity yet.")

    # ==================================================
    # 6️⃣ CHART OF ACCOUNTS
    # ==================================================
    with tabs[5]:

        st.subheader("Chart of Accounts")

        st.dataframe(accounts_df)

        st.download_button(
            label="Download COA (CSV)",
            data=accounts_df.to_csv(index=False),
            file_name="chart_of_accounts.csv",
            mime="text/csv",
            key="coa_download"
        )

    # ==================================================
    # 7️⃣ PERIOD CONTROL
    # ==================================================
    with tabs[6]:

        st.subheader("Accounting Period Control")

        closed_through = get_closed_through()

        if closed_through:
            st.info(f"Closed through: {closed_through}")
        else:
            st.info("No periods closed.")

        close_date = st.date_input("Close Through Date", key="close_date")

        if st.button("Close Period Through Date", key="close_btn"):

            close_through(close_date)
            log_action("Period Closed", f"Closed through {close_date}")

            st.success(f"Period closed through {close_date}")
