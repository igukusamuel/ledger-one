import streamlit as st
from datetime import date

from core.accruals import accrued_interest
from core.journals import generate_accrual_journal, JournalEntry
from core.periods import is_period_open
from core.batch import batch_accruals
from core.reconciliation import accrual_cash_recon
from core.reversals import reverse_accrual


# ------------------------------------------------
# Initialization
# ------------------------------------------------

def init_subledger():
    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = []

    if "closed_periods" not in st.session_state:
        st.session_state.closed_periods = set()

    if "accrual_registry" not in st.session_state:
        # (trade_id, date) to prevent duplicate accruals
        st.session_state.accrual_registry = set()


# ------------------------------------------------
# Helpers
# ------------------------------------------------

def get_active_trade():
    if "active_trade_id" not in st.session_state:
        return None

    return next(
        (t for t in st.session_state.trades
         if t["trade_id"] == st.session_state.active_trade_id),
        None
    )


# ------------------------------------------------
# Journal Display
# ------------------------------------------------

def show_journals():
    st.subheader("Journal Entries")

    if not st.session_state.journal_entries:
        st.info("No journal entries posted.")
        return

    st.dataframe([{
        "Date": j.date,
        "Account": j.account,
        "Debit": j.debit,
        "Credit": j.credit,
        "Description": j.description,
        "Source": j.source,
        "Trade ID": j.trade_id
    } for j in st.session_state.journal_entries])


# ------------------------------------------------
# Manual Journal Entry
# ------------------------------------------------

def manual_entry_ui():
    st.subheader("Manual Journal Entry")

    with st.form("manual_entry_form"):
        account = st.text_input("Account")
        debit = st.number_input("Debit", min_value=0.0)
        credit = st.number_input("Credit", min_value=0.0)
        description = st.text_input("Description")

        submitted = st.form_submit_button("Post Entry")

        if submitted:
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
            st.success("Manual journal entry posted.")


# ------------------------------------------------
# Accrual Engine
# ------------------------------------------------

def accrual_ui():
    st.subheader("Interest Accrual")

    active_trade = get_active_trade()

    if not active_trade:
        st.info("No active trade selected.")
        return

    if st.button("Generate Daily Accrual"):
        valuation_date = date.today()

        # Period Lock Check
        if not is_period_open(
            valuation_date,
            st.session_state.closed_periods
        ):
            st.error("Accounting period is closed.")
            return

        registry_key = (
            active_trade["trade_id"],
            valuation_date
        )

        # Duplicate Protection
        if registry_key in st.session_state.accrual_registry:
            st.warning("Accrual already generated for this trade/date.")
            return

        accrual_amount = accrued_interest(
            active_trade["last_coupon_date"],
            valuation_date,
            active_trade["coupon_amount"]
        )

        journals = generate_accrual_journal(
            valuation_date,
            accrual_amount
        )

        for j in journals:
            j.trade_id = active_trade["trade_id"]

        st.session_state.journal_entries.extend(journals)
        st.session_state.accrual_registry.add(registry_key)

        st.success(f"Accrued interest: {round(accrual_amount, 2)}")


    # Batch Accrual
    if st.button("Generate Month-End Accruals"):
        start_date = active_trade["last_coupon_date"]
        end_date = date.today()

        def accrual_func(d):
            registry_key = (active_trade["trade_id"], d)

            if registry_key in st.session_state.accrual_registry:
                return []

            amount = accrued_interest(
                active_trade["last_coupon_date"],
                d,
                active_trade["coupon_amount"]
            )

            journals = generate_accrual_journal(d, amount)

            for j in journals:
                j.trade_id = active_trade["trade_id"]

            st.session_state.accrual_registry.add(registry_key)

            return journals

        journals = batch_accruals(
            start_date,
            end_date,
            accrual_func
        )

        st.session_state.journal_entries.extend(journals)
        st.success("Batch accruals generated.")


# ------------------------------------------------
# Coupon Payment & Reversal
# ------------------------------------------------

def coupon_payment_ui():
    st.subheader("Coupon Payment")

    active_trade = get_active_trade()

    if not active_trade:
        return

    if st.button("Post Coupon Payment"):
        payment_date = date.today()

        # Reverse accrued interest
        for j in list(st.session_state.journal_entries):
            if (
                j.account == "Interest Receivable"
                and j.trade_id == active_trade["trade_id"]
            ):
                reversal = reverse_accrual(j, payment_date)
                st.session_state.journal_entries.append(reversal)

        # Cash receipt
        st.session_state.journal_entries.append(
            JournalEntry(
                date=payment_date,
                account="Cash",
                debit=active_trade["coupon_amount"],
                description="Coupon received",
                source="SYSTEM",
                trade_id=active_trade["trade_id"]
            )
        )

        st.success("Coupon posted and accruals reversed.")


# ------------------------------------------------
# Period Close
# ------------------------------------------------

def period_close_ui():
    st.subheader("Period Close")

    if st.button("Close Today"):
        st.session_state.closed_periods.add(date.today())
        st.success("Period closed.")


# ------------------------------------------------
# Trial Balance
# ------------------------------------------------

def trial_balance_ui():
    st.subheader("Trial Balance")

    tb = {}

    for j in st.session_state.journal_entries:
        tb[j.account] = tb.get(j.account, 0) + j.debit - j.credit

    st.dataframe([
        {"Account": acc, "Balance": round(balance, 2)}
        for acc, balance in tb.items()
    ])


# ------------------------------------------------
# Accrual vs Cash Reconciliation
# ------------------------------------------------

def reconciliation_ui():
    st.subheader("Accrual vs Cash Reconciliation")

    recon = accrual_cash_recon(
        st.session_state.journal_entries
    )

    st.table(recon)


# ------------------------------------------------
# Main Render
# ------------------------------------------------

def render():
    init_subledger()

    st.header("Subledger")

    show_journals()
    manual_entry_ui()
    accrual_ui()
    coupon_payment_ui()
    period_close_ui()
    trial_balance_ui()
    reconciliation_ui()
