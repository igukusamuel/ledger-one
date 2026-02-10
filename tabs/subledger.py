import streamlit as st
from datetime import date

from core.accruals import accrued_interest
from core.journals import generate_accrual_journal

from core.periods import is_period_open
from core.batch import batch_accruals

from core.reconciliation import accrual_cash_recon




# ---------- Helpers ----------

def init_subledger():
    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = []

    if "closed_periods" not in st.session_state:
        st.session_state.closed_periods = set()

def show_journals():
    st.subheader("Journal Entries")
    if not st.session_state.journal_entries:
        st.info("No journal entries yet.")
        return

    st.dataframe([
        {
            "Date": j.date,
            "Account": j.account,
            "Debit": j.debit,
            "Credit": j.credit,
            "Description": j.description,
            "Source": j.source
        }
        for j in st.session_state.journal_entries
    ])

def manual_entry_ui():
    st.subheader("Manual Journal Entry")

    with st.form("manual_journal"):
        account = st.text_input("Account")
        debit = st.number_input("Debit", min_value=0.0, step=0.01)
        credit = st.number_input("Credit", min_value=0.0, step=0.01)
        description = st.text_input("Description")

        submitted = st.form_submit_button("Post Entry")

        if submitted:
            st.session_state.journal_entries.append(
                generate_accrual_journal(
                    accrual_date=date.today(),
                    amount=0
                )[0].__class__(
                    date=date.today(),
                    account=account,
                    debit=debit,
                    credit=credit,
                    description=description,
                    source="MANUAL"
                )
            )
            st.success("Manual journal posted.")





# ---------- NEW: Accrual Section ----------

def accrual_ui():
    st.subheader("Interest Accrual")

    if st.button("Generate Daily Accrual"):
        valuation_date = date.today()

        if not is_period_open(
            valuation_date,
            st.session_state["closed_periods"]
        ):
            st.error("Accounting period is closed. Accruals are locked.")
            return

        accrual_amount = accrued_interest(
            last_coupon_date=st.session_state["last_coupon_date"],
            valuation_date=valuation_date,
            coupon_amount=st.session_state["coupon_amount"]
        )

        journals = generate_accrual_journal(
            accrual_date=valuation_date,
            amount=accrual_amount
        )

        st.session_state.journal_entries.extend(journals)
        st.success(f"Accrued interest posted: {accrual_amount}")

    if st.button("Generate Month-End Accruals"):
        journals = batch_accruals(
            start_date=st.session_state["last_coupon_date"],
            end_date=date.today(),
            accrual_func=lambda d: generate_accrual_journal(
                d,
                accrued_interest(
                    st.session_state["last_coupon_date"],
                    d,
                    st.session_state["coupon_amount"]
                )
            )
        )
    
        st.session_state.journal_entries.extend(journals)
        st.success("Batch accruals generated.")


# ---------- period close ----------

def period_close_ui():
    st.subheader("Period Close")

    if st.button("Close Today"):
        st.session_state.closed_periods.add(date.today())
        st.success("Accounting period closed.")


# ---------- Trial Balance ----------

def trial_balance_ui():
    st.subheader("Trial Balance")

    tb = {}
    for j in st.session_state.journal_entries:
        tb[j.account] = tb.get(j.account, 0) + j.debit - j.credit

    st.dataframe([
        {"Account": k, "Balance": round(v, 2)}
        for k, v in tb.items()
    ])

    st.subheader("Accrual vs Cash Reconciliation")
    
    recon = accrual_cash_recon(st.session_state.journal_entries)
    st.table(recon)

---------- Coupon payment ----------

def coupon_payment_ui():
    st.subheader("Coupon Payment")

    if st.button("Post Coupon Payment"):
        payment_date = date.today()
        coupon_amount = st.session_state["coupon_amount"]

        # Reverse all open accruals
        accruals = [
            j for j in st.session_state.journal_entries
            if j.account == "Interest Receivable" and j.source == "SYSTEM"
        ]

        for a in accruals:
            st.session_state.journal_entries.append(
                reverse_accrual(a, payment_date)
            )

        # Cash receipt
        st.session_state.journal_entries.append(
            JournalEntry(
                date=payment_date,
                account="Cash",
                debit=coupon_amount,
                description="Coupon received",
                source="SYSTEM"
            )
        )

        st.success("Coupon payment posted and accruals reversed.")


# ---------- Main Render ----------

def render():
    init_subledger()
    show_journals()
    manual_entry_ui()
    accrual_ui()
    period_close_ui()
    trial_balance_ui()
