import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(layout="wide", page_title="LedgerOne Café Test")

st.title("LedgerOne ERP System – Café Test Environment")
st.write("APP LOADED")

# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

from core.persistence import initialize_db
initialize_db()

st.write("DATABASE INITIALIZED")

# --------------------------------------------------
# IMPORT CORE MODULES
# --------------------------------------------------

from core.persistence import load_journals
from core.journals import JournalEntry
from core.inventory import init_inventory, get_inventory, update_inventory
from core.pos_gl import post_sale_to_gl
from core.auth import authenticate

# --------------------------------------------------
# INIT SESSION STATE
# --------------------------------------------------

def init_app():
    init_inventory()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "cart" not in st.session_state:
        st.session_state.cart = []

init_app()

# --------------------------------------------------
# LOGIN SCREEN
# --------------------------------------------------

def login_screen():

    st.header("☕ Café POS Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = authenticate(username, password)

        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.rerun()
        else:
            st.error("Invalid credentials")

# --------------------------------------------------
# POS SCREEN
# --------------------------------------------------

def pos_screen():

    st.header("☕ Café Store")

    inventory = get_inventory()

    if inventory.empty:
        st.warning("Inventory not available.")
        return

    col_products, col_cart = st.columns([2, 1])

    # ---------------- PRODUCTS ----------------
    with col_products:

        st.subheader("Products")

        categories = inventory["category"].unique()
        selected_category = st.selectbox("Category", categories)

        subcategories = inventory[
            inventory["category"] == selected_category
        ]["subcategory"].unique()

        selected_subcategory = st.selectbox("Subcategory", subcategories)

        filtered = inventory[
            (inventory["category"] == selected_category) &
            (inventory["subcategory"] == selected_subcategory)
        ]

        for _, row in filtered.iterrows():

            col_item, col_qty = st.columns([3, 1])

            with col_item:
                st.write(f"**{row['product']}** — ${row['price']}")
                st.caption(f"Stock: {row['stock']}")

            with col_qty:

                qty = st.number_input(
                    "",
                    min_value=1,
                    max_value=row["stock"] if row["stock"] > 0 else 1,
                    value=1,
                    key=f"qty_{row['product']}"
                )

                if st.button("Add", key=f"add_{row['product']}"):

                    if row["stock"] < qty:
                        st.error("Insufficient stock.")
                    else:
                        st.session_state.cart.append({
                            "product": row["product"],
                            "price": row["price"],
                            "quantity": qty,
                            "total": row["price"] * qty,
                            "cogs": row["cost"] * qty
                        })
                        st.success("Added to cart")

    # ---------------- CART ----------------
    with col_cart:

        st.subheader("Cart")

        if not st.session_state.cart:
            st.info("Cart empty.")
            return

        df = pd.DataFrame(st.session_state.cart)

        display_df = df[["product", "quantity", "price", "total"]]
        st.dataframe(display_df, use_container_width=True)

        subtotal = df["total"].sum()
        tax = round(subtotal * 0.07, 2)
        total = round(subtotal + tax, 2)
        total_cogs = df["cogs"].sum()

        st.markdown("---")
        st.write(f"Subtotal: ${subtotal}")
        st.write(f"Tax (7%): ${tax}")
        st.write(f"**Total: ${total}**")

        payment = st.selectbox("Payment Type", ["Cash", "Card"])

        if st.button("Checkout"):

            # Double-check stock
            for item in st.session_state.cart:
                stock = inventory.loc[
                    inventory["product"] == item["product"],
                    "stock"
                ].values[0]

                if stock < item["quantity"]:
                    st.error(f"Insufficient stock for {item['product']}")
                    return

            # Reduce inventory
            for item in st.session_state.cart:
                update_inventory(item["product"], item["quantity"])

            # Post to GL
            post_sale_to_gl(
                entity_id="CAFE",
                total=total,
                tax=tax,
                revenue=subtotal,
                cogs=total_cogs,
                payment_type=payment
            )

            st.success("Sale Completed")
            st.session_state.cart = []
            st.rerun()

# --------------------------------------------------
# LEDGER VIEW
# --------------------------------------------------

def ledger_view():

    st.markdown("---")
    st.header("📘 General Ledger – CAFE Entity")

    journals = load_journals(JournalEntry)

    if not journals:
        st.info("No journal entries posted yet.")
        return

    cafe_journals = [j for j in journals if j.entity_id == "CAFE"]

    if not cafe_journals:
        st.info("No Cafe postings yet.")
        return

    ledger_rows = []

    for j in cafe_journals:

        ledger_rows.append({
            "Date": j.entry_date,
            "Account": j.debit_account,
            "Debit": j.amount,
            "Credit": 0.0
        })

        ledger_rows.append({
            "Date": j.entry_date,
            "Account": j.credit_account,
            "Debit": 0.0,
            "Credit": j.amount
        })

    df = pd.DataFrame(ledger_rows)
    df = df.sort_values("Date")

    df["Balance"] = (
        df.groupby("Account")["Debit"].cumsum() -
        df.groupby("Account")["Credit"].cumsum()
    )

    st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# MAIN ROUTING
# --------------------------------------------------

if not st.session_state.logged_in:
    login_screen()
else:
    pos_screen()
    ledger_view()
