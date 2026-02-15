import streamlit as st
import pandas as pd
from datetime import date

from core.pos import record_sale
from core.persistence import load_journals, save_journals
from core.journals import JournalEntry
from core.entities import get_entities

st.subheader("Add Items to Cart")

sku = st.selectbox("SKU", ["LATTE", "CROISSANT"], key="sku")
price = st.number_input("Unit Price", min_value=0.0, key="price")
quantity = st.number_input("Quantity", min_value=1, key="qty")

if "cart" not in st.session_state:
    st.session_state.cart = []

if st.button("Add to Cart"):
    st.session_state.cart.append({
        "sku": sku,
        "price": price,
        "quantity": quantity
    })

st.write("Cart:", st.session_state.cart)

tax_rate = st.number_input("Sales Tax Rate (e.g. 0.08)", value=0.08)

if st.button("Finalize Sale"):

    journals, total = record_sale(entity_id, st.session_state.cart, tax_rate)

    for j in journals:
        j.entry_date = str(sale_date)

    all_journals = load_journals(JournalEntry)
    all_journals.extend(journals)
    save_journals(all_journals)

    st.success(f"Sale completed. Total charged: {round(total,2)}")

    st.session_state.cart = []

def render():

    st.header("Coffee Café PoS Module")

    journals = load_journals(JournalEntry)

    entities = get_entities()
    entity_map = {f"{e[1]} - {e[2]}": e[0] for e in entities}

    selected_entity = st.selectbox(
        "Select Entity",
        list(entity_map.keys()),
        key="cafe_entity"
    )

    entity_id = entity_map[selected_entity]

    sale_date = st.date_input("Sale Date", value=date.today(), key="cafe_date")

    sale_amount = st.number_input(
        "Total Sale Amount",
        min_value=0.0,
        key="cafe_sale"
    )

    cost_amount = st.number_input(
        "Cost of Goods",
        min_value=0.0,
        key="cafe_cost"
    )

    if st.button("Record Sale", key="record_sale_btn"):

        new_journals = record_sale(entity_id, sale_amount, cost_amount)

        # assign date
        for j in new_journals:
            j.entry_date = str(sale_date)

        journals.extend(new_journals)
        save_journals(journals)

        st.success("Sale recorded and posted to GL.")

    st.divider()

    st.subheader("Today's Sales Summary")

    df = pd.DataFrame([
        {
            "Date": j.entry_date,
            "Debit": j.debit_account,
            "Credit": j.credit_account,
            "Amount": j.amount
        }
        for j in journals
        if j.description == "Cafe Sale"
        and j.entity_id == entity_id
    ])

    if not df.empty:
        st.dataframe(df)
        st.metric("Total Sales", round(df["Amount"].sum(), 2))
    else:
        st.info("No café sales recorded.")
