import streamlit as st
from datetime import date

from core.accruals import accrued_interest
from core.journals import generate_accrual_journal, JournalEntry
from core.periods import is_period_open
from core.batch import batch_accruals
from core.reconciliation import accrual_cash_recon
from core.reversals import reverse_accrual


def init_subledger():
    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = []
    if "closed_periods" not in st.session_state:
        st.session_state.closed_periods = set()


def show_journals():
    st.subheader("Journal Entries")
    if not st.session_state.journal_entries:
        st.info("No journal entries.")
        return

    st.dataframe([{
        "Date": j.date,
        "Account": j.account,
        "Debit": j.debit,
        "Credit": j.credit,
        "Description": j.description,
        "Source": j.source
    } for j in st.session_state.journal_entries])


def manual_entry_ui():
    st.subheader("Manual Journal Entry")

    with st.form("manual_entry"):
        account = st.text_input("Account")
        debit = st.number_input("Debit", min_value=0.0)
        credit = st.number_input("Credit", min_value=0.0)
        description = st.text_input("Description")

        if st.form_submit_button("Post Entry"):
            st.session_state.journal_entries.append(
                JournalEntry(
                    date=date.today(),
                    account=account,
                    debit=debit,
                    credit=credit,
                    description=description,
                    source="MANUAL"
                )
            )
            st.success("Manual entry posted.")


def accrual_ui():
    st.subheader("Interest Accrual")

    if "last_coupon_date" not in st.session_state:
        st.info("No trade data available for accruals.")
        return

    if st.button("Generate Daily Accrual"):
        valuation_date = date.today()

        if not is_period_open(valuation_date, st.session_state.closed_periods):
            st.error("Period closed.")
            return

        accrual = accrued_interest(
            st.session_state["last_coupon_date"],
            valuation_date,
            st.session_state["coupon_amount"]
        )

        st.session_state.journal_entries.extend(
            generate_accrual_journal(valuation_date, accrual)
        )
        st.success(f"Accrued {accrual}")


def period_close_ui():
    st.subheader("Period Close")
    if st.button("Close Today"):
        st.session_state.closed_periods.add(date.today())
        st.success("Period closed.")


def trial_balance_ui():
    st.subheader("Trial Balance")
    tb = {}
    for j in st.session_state.journal_entries:
        tb[j.account] = tb.get(j.account, 0) + j.debit - j.credit
    st.dataframe([{"Account": k, "Balance": v} for k, v in tb.items()])


def render():
    init_subledger()
    show_journals()
    manual_entry_ui()
    accrual_ui()
    period_close_ui()
    trial_balance_ui()
