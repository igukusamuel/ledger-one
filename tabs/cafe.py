import streamlit as st
from core.pos import record_sale
from core.persistence import load_journals, save_journals
from core.journals import JournalEntry
from core.inventory import add_inventory_item
from core.persistence import load_inventory


def render():

    st.header("Coffee Cafe - POS")

    entity_id = "CAFE_ENTITY"

    # -------------------------
    # Inventory Setup
    # -------------------------

    st.subheader("Add Inventory Item")

    sku = st.text_input("SKU")
    name = st.text_input("Item Name")
    quantity = st.number_input("Initial Quantity", min_value=0)
    unit_cost = st.number_input("Unit Cost", min_value=0.0)

    if st.button("Add Inventory"):
        add_inventory_item(sku, name, quantity, unit_cost)
        st.success("Inventory Added")

    inventory = load_inventory()

    st.subheader("Current Inventory")
    st.write(inventory)

    # -------------------------
    # POS
    # -------------------------

    st.subheader("Create Sale")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    available_skus = list(inventory.keys())

    if available_skus:

        selected_sku = st.selectbox("Select SKU", available_skus)
        price = st.number_input("Unit Price", min_value=0.0)
        qty = st.number_input("Quantity", min_value=1)

        if st.button("Add to Cart"):
            st.session_state.cart.append({
                "sku": selected_sku,
                "price": price,
                "quantity": qty
            })

        st.write("Cart:", st.session_state.cart)

        tax_rate = st.number_input("Sales Tax Rate", value=0.08)

        if st.button("Finalize Sale"):
            journals, total = record_sale(entity_id, st.session_state.cart, tax_rate)

            existing = load_journals(JournalEntry)
            existing.extend(journals)
            save_journals(existing)

            st.success(f"Sale Complete. Total: {round(total,2)}")
            st.session_state.cart = []
