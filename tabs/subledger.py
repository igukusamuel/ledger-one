import streamlit as st
from datetime import date

from core.accruals import accrued_interest
from core.journals import generate_accrual_journal

# ---------- Helpers ----------

def init_subledger():
    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = []

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
    st.subheader("Interest Accrual (System Generated)")

    if "last_coupon_date" not in st.session_state:
        st.warning("No trade data available for accruals.")
        return

    if st.button("Generate Daily Accrual"):
        valuation_date = date.today()

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

# ---------- Main Render ----------

def render():
    init_subledger()
    show_journals()
    manual_entry_ui()
    accrual_ui()        # ← INSERTED, NOT REPLACED
    trial_balance_ui()
