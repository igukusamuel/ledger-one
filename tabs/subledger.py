import streamlit as st
import pandas as pd
from datetime import date

from core.journals import JournalEntry
from core.accruals import generate_accrual_journal
from core.batch import batch_accruals
from core.gl import post_to_gl, generate_trial_balance
from core.persistence import load_journals, save_journals
from core.audit import log_action
from core.chart_of_accounts import get_account_type

if st.button("Post Entry"):

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

        st.success("Posted.")

def init_subledger():

    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = load_journals(JournalEntry)

    if "period_closed" not in st.session_state:
        st.session_state.period_closed = False


def render():

    init_subledger()

    st.header("Subledger")

    tabs = st.tabs([
        "Manual Entry",
        "Accrual Generator",
        "Batch Accruals",
        "Trial Balance",
        "Audit Log"
    ])

    # ===============================
    # Manual Entry
    # ===============================
    with tabs[0]:

        if st.session_state.period_closed:
            st.warning("Period closed.")
        else:

            entry_date = st.date_input("Entry Date", value=date.today())
            debit = st.text_input("Debit Account")
            credit = st.text_input("Credit Account")
            amount = st.number_input("Amount", min_value=0.0)

            if st.button("Post Entry", key="manual_post_entry"):

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

                st.success("Posted.")

    # ===============================
    # Accrual Generator
    # ===============================
    with tabs[1]:

        if not st.session_state.get("trades"):
            st.info("No trades captured.")
        else:

            trade_ids = [t["trade_id"] for t in st.session_state.trades]
            selected_trade = st.selectbox("Trade", trade_ids)

            start = st.date_input("Start Date")
            end = st.date_input("End Date")

            if st.button("Generate Accrual", key="generate_accrual"):

                trade = next(
                    t for t in st.session_state.trades
                    if t["trade_id"] == selected_trade
                )

                journal = generate_accrual_journal(trade, start, end)

                st.session_state.journal_entries.append(journal)
                save_journals(st.session_state.journal_entries)

                log_action("Accrual Generated", f"{selected_trade}")

                st.success("Accrual posted.")

    # ===============================
    # Batch Accruals
    # ===============================
    with tabs[2]:

        cutoff = st.date_input("Cutoff Date", value=date.today())

        if st.button("Run Batch", key="run_batch"):

            journals = batch_accruals(
                st.session_state.trades,
                cutoff
            )

            st.session_state.journal_entries.extend(journals)
            save_journals(st.session_state.journal_entries)

            log_action("Batch Accrual", f"{len(journals)} entries")

            st.success(f"{len(journals)} accruals generated.")

    # ===============================
    # Trial Balance + Excel Export
    # ===============================
    with tabs[3]:

        tb = generate_trial_balance(st.session_state.journal_entries)

        df = pd.DataFrame(tb)

        if not df.empty:
            st.dataframe(df)

            st.download_button(
                "Download Trial Balance (Excel)",
                key="download_trial_balance",
                df.to_csv(index=False),
                file_name="trial_balance.csv",
                mime="text/csv"
            )
        else:
            st.info("No data.")

    # ===============================
    # Audit Log
    # ===============================
    with tabs[4]:

        from core.audit import load_audit_log

        logs = load_audit_log()

        if logs:
            df = pd.DataFrame(logs, columns=["Timestamp", "Action", "Details"])
            st.dataframe(df)
        else:
            st.info("No audit activity.")
