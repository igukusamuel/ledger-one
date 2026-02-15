import streamlit as st
import pandas as pd
from datetime import date

from core.journals import JournalEntry
from core.accruals import generate_accrual_journal
from core.batch import batch_accruals
from core.gl import post_to_gl
from core.persistence import load_journals, save_journals


# ---------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------

def init_subledger():

    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = load_journals(JournalEntry)

    if "period_closed" not in st.session_state:
        st.session_state.period_closed = False


# ---------------------------------------------------
# MAIN RENDER FUNCTION
# ---------------------------------------------------

def render():

    init_subledger()

    st.header("Subledger")

    tabs = st.tabs([
        "Manual Journal",
        "Accrual Generator",
        "Batch Accruals",
        "Reconciliation",
        "Post to GL"
    ])

    # ==================================================
    # 1️⃣ MANUAL JOURNAL ENTRY
    # ==================================================
    with tabs[0]:

        st.subheader("Manual Journal Entry")

        if st.session_state.period_closed:
            st.warning("Period is closed. Manual postings disabled.")
        else:
            entry_date = st.date_input("Entry Date", value=date.today())
            debit_account = st.text_input("Debit Account")
            credit_account = st.text_input("Credit Account")
            amount = st.number_input("Amount", min_value=0.0)

            if st.button("Post Manual Entry"):

                journal = JournalEntry(
                    entry_date=str(entry_date),
                    debit_account=debit_account,
                    credit_account=credit_account,
                    amount=amount,
                    description="Manual Entry"
                )

                st.session_state.journal_entries.append(journal)
                save_journals(st.session_state.journal_entries)

                st.success("Manual journal posted.")

    # ==================================================
    # 2️⃣ ACCRUAL GENERATOR
    # ==================================================
    with tabs[1]:

        st.subheader("Accrual Generator")

        if not st.session_state.get("trades"):
            st.info("No trades available. Capture a bond first.")
        else:

            trade_ids = [t["trade_id"] for t in st.session_state.trades]
            selected_trade = st.selectbox("Select Trade", trade_ids)

            accrual_start = st.date_input("Accrual Start Date")
            accrual_end = st.date_input("Accrual End Date")

            auto_reverse = st.checkbox("Auto-reverse on coupon date", value=True)

            if st.button("Generate Accrual"):

                if st.session_state.period_closed:
                    st.error("Period is closed. Accruals disabled.")
                else:

                    trade = next(
                        t for t in st.session_state.trades
                        if t["trade_id"] == selected_trade
                    )

                    journal = generate_accrual_journal(
                        trade,
                        accrual_start,
                        accrual_end,
                        auto_reverse=auto_reverse
                    )

                    st.session_state.journal_entries.append(journal)
                    save_journals(st.session_state.journal_entries)

                    st.success("Accrual posted.")

    # ==================================================
    # 3️⃣ BATCH ACCRUALS
    # ==================================================
    with tabs[2]:

        st.subheader("Batch Accrual Generation")

        batch_date = st.date_input("Accrual Cutoff Date", value=date.today())

        if st.button("Run Batch Accruals"):

            if st.session_state.period_closed:
                st.error("Period is closed. Batch disabled.")
            else:

                journals = batch_accruals(
                    st.session_state.trades,
                    batch_date
                )

                st.session_state.journal_entries.extend(journals)
                save_journals(st.session_state.journal_entries)

                st.success(f"{len(journals)} accruals generated.")

    # ==================================================
    # 4️⃣ ACCRUAL VS CASH RECON
    # ==================================================
    with tabs[3]:

        st.subheader("Accrual vs Cash Reconciliation")

        data = []

        for j in st.session_state.journal_entries:
            data.append({
                "Date": j.entry_date,
                "Debit": j.debit_account,
                "Credit": j.credit_account,
                "Amount": j.amount,
                "Description": j.description
            })

        df = pd.DataFrame(data)

        if not df.empty:

            accrual_total = df[df["Debit"] == "Interest Receivable"]["Amount"].sum()
            cash_total = df[df["Debit"] == "Cash"]["Amount"].sum()

            st.metric("Total Accrued Interest", round(accrual_total, 2))
            st.metric("Total Cash Received", round(cash_total, 2))
            st.metric("Difference", round(accrual_total - cash_total, 2))

            st.dataframe(df)

        else:
            st.info("No journal entries yet.")

    # ==================================================
    # 5️⃣ POST TO GENERAL LEDGER
    # ==================================================
    with tabs[4]:

        st.subheader("General Ledger Posting")

        if st.button("Post to GL"):

            gl = post_to_gl(st.session_state.journal_entries)

            df = pd.DataFrame([
                {"Account": k, "Balance": round(v, 2)}
                for k, v in gl.items()
            ])

            st.dataframe(df)

    # ==================================================
    # PERIOD CLOSE CONTROL
    # ==================================================
    st.divider()
    st.subheader("Period Controls")

    if not st.session_state.period_closed:
        if st.button("Close Period"):
            st.session_state.period_closed = True
            st.success("Period closed. Postings disabled.")
    else:
        if st.button("Reopen Period"):
            st.session_state.period_closed = False
            st.success("Period reopened.")
