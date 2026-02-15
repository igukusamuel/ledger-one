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


# ---------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------

def init_subledger():

    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = load_journals(JournalEntry)

    if "period_closed" not in st.session_state:
        st.session_state.period_closed = False


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
    # 1️⃣ MANUAL JOURNAL ENTRY
    # ==================================================
    with tabs[0]:

        st.subheader("Manual Journal Entry")

        if st.session_state.period_closed:
            st.warning("Period is closed. Posting disabled.")
        else:

            entry_date = st.date_input("Entry Date", value=date.today(), key="manual_date")
            debit = st.text_input("Debit Account", key="manual_debit")
            credit = st.text_input("Credit Account", key="manual_credit")
            amount = st.number_input("Amount", min_value=0.0, key="manual_amount")

            if st.button("Post Entry", key="manual_post_entry"):

                if not get_account_type(debit):
                    st.error("Invalid debit account.")
                elif not get_account_type(credit):
                    st.error("Invalid credit account.")
                else:

                    journal = JournalEntry(
                        str(entry_date),
                        debit,
                        credit,
                        amount,
                        "Manual Entry"
                    )

                    st.session_state.journal_entries.append(journal)
                    save_journals(st.session_state.journal_entries)

                    log_action("Manual Entry", f"{debit}/{credit} {amount}")

                    st.success("Manual journal posted.")

    # ==================================================
    # 2️⃣ ACCRUAL GENERATOR
    # ==================================================
    with tabs[1]:

        st.subheader("Single Accrual")

        if not st.session_state.get("trades"):
            st.info("No trades available.")
        else:

            trade_ids = [t["trade_id"] for t in st.session_state.trades]

            selected_trade = st.selectbox(
                "Select Trade",
                trade_ids,
                key="accrual_trade_select"
            )

            start = st.date_input("Start Date", key="accrual_start")
            end = st.date_input("End Date", key="accrual_end")

            if st.button("Generate Accrual", key="generate_accrual_btn"):

                if st.session_state.period_closed:
                    st.error("Period closed.")
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

        st.subheader("Batch Accrual Engine")

        cutoff = st.date_input("Cutoff Date", value=date.today(), key="batch_cutoff")

        if st.button("Run Batch", key="run_batch_btn"):

            if st.session_state.period_closed:
                st.error("Period closed.")
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

        st.subheader("Trial Balance")

        tb = generate_trial_balance(st.session_state.journal_entries)

        df = pd.DataFrame(tb)

        if not df.empty:

            st.dataframe(df)

            st.download_button(
                label="Download Trial Balance (CSV)",
                data=df.to_csv(index=False),
                file_name="trial_balance.csv",
                mime="text/csv",
                key="download_tb"
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
    # 6️⃣ PERIOD CONTROL
    # ==================================================
    with tabs[5]:

        st.subheader("Accounting Period Control")

        if not st.session_state.period_closed:

            if st.button("Close Period", key="close_period_btn"):
                st.session_state.period_closed = True
                log_action("Period Closed", "User triggered period close")
                st.success("Period closed.")

        else:

            st.warning("Period is currently closed.")

            if st.button("Reopen Period", key="reopen_period_btn"):
                st.session_state.period_closed = False
                log_action("Period Reopened", "User reopened period")
                st.success("Period reopened.")
