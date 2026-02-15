import streamlit as st
import pandas as pd
from datetime import date

from core.pos import record_sale
from core.persistence import load_journals, save_journals
from core.journals import JournalEntry
from core.entities import get_entities


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
