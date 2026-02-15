import streamlit as st
import pandas as pd
from datetime import date

from core.journals import JournalEntry
from core.accruals import generate_accrual_journal
from core.batch import batch_accruals
from core.gl import generate_trial_balance
from core.persistence import load_journals, save_journals
from core.audit import log_action, load_audit_log
from core.chart_of_accounts import get_account_type
from core.periods import get_closed_through, close_through

from core.entities import get_entities
from core.chart_of_accounts import get_accounts



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
        "Period Control"
    ])

    # ==================================================
    # 1️⃣ MANUAL ENTRY
    # ==================================================
   entities = get_entities()
entity_options = {f"{e[1]} - {e[2]}": e[0] for e in entities}

selected_entity = st.selectbox(
    "Select Entity",
    list(entity_options.keys()),
    key="entity_select"
)

entity_id = entity_options[selected_entity]

accounts_df = get_accounts()
account_codes = accounts_df["account_code"].tolist()

entry_date = st.date_input("Entry Date")

debit = st.selectbox(
    "Debit Account",
    account_codes,
    key="debit_dropdown"
)

credit = st.selectbox(
    "Credit Account",
    account_codes,
    key="credit_dropdown"
)

amount = st.number_input("Amount", min_value=0.0)

if st.button("Post Entry", key="manual_post_multi"):

    closed_through = get_closed_through()

    if closed_through and entry_date <= closed_through:
        st.error("Period closed.")
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

        st.success("Posted.")

        # ==================================================
    # 2️⃣ CHART OF ACCOUNTS
    # ==================================================

with tabs[6]:

    st.subheader("Chart of Accounts")

    df = get_accounts()

    st.dataframe(df)

    st.download_button(
        label="Download COA (Excel)",
        data=df.to_csv(index=False),
        file_name="chart_of_accounts.csv",
        mime="text/csv"
    )


    # ==================================================
    # 2️⃣ ACCRUAL GENERATOR
    # ==================================================
    with tabs[1]:

        if not st.session_state.get("trades"):
            st.info("No trades available.")
        else:

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

                    journal = generate_accrual_journal(trade, start, end)

                    st.session_state.journal_entries.append(journal)
                    save_journals(st.session_state.journal_entries)

                    log_action("Accrual Generated", selected_trade)

                    st.success("Accrual posted.")

    # ==================================================
    # 3️⃣ BATCH ACCRUALS
    # ==================================================
    with tabs[2]:

        cutoff = st.date_input("Cutoff Date", value=date.today(), key="batch_cutoff")

        if st.button("Run Batch", key="batch_btn"):

            closed_through = get_closed_through()

            if closed_through and cutoff <= closed_through:
                st.error("Batch date is within closed period.")
            else:

                journals = batch_accruals(
                    st.session_state.get("trades", []),
                    cutoff
                )

                st.session_state.journal_entries.extend(journals)
                save_journals(st.session_state.journal_entries)

                log_action("Batch Accrual", f"{len(journals)} entries")

                st.success(f"{len(journals)} accruals generated.")

    # ==================================================
    # 4️⃣ TRIAL BALANCE
    # ==================================================
    with tabs[3]:

        tb = generate_trial_balance(st.session_state.journal_entries)
        df = pd.DataFrame(tb)

        if not df.empty:
            st.dataframe(df)

            st.download_button(
                label="Download Trial Balance (CSV)",
                data=df.to_csv(index=False),
                file_name="trial_balance.csv",
                mime="text/csv",
                key="tb_download"
            )
        else:
            st.info("No journal data available.")

    # ==================================================
    # 5️⃣ AUDIT LOG
    # ==================================================
    with tabs[4]:

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
    # 6️⃣ PERIOD CONTROL
    # ==================================================
    with tabs[5]:

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
