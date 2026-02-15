import streamlit as st
import pandas as pd
from datetime import datetime
from core.auth import authenticate
from core.inventory import (
    init_inventory,
    seed_inventory,
    get_inventory,
    update_inventory,
)
from core.pos_gl import post_sale_to_gl


# --------------------------------------------------
# INIT
# --------------------------------------------------

def init_pos():

    init_inventory()
    seed_inventory()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "cart" not in st.session_state:
        st.session_state.cart = []

    if "daily_sales" not in st.session_state:
        st.session_state.daily_sales = []


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

def login():

    st.title("☕ LedgerOne Café POS")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        role = authenticate(username, password)

        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials")


# --------------------------------------------------
# POS
# --------------------------------------------------

def pos_screen():

    st.title("☕ Coffee Café POS")

    st.sidebar.write(f"User: {st.session_state.username}")
    st.sidebar.write(f"Role: {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.cart = []
        st.rerun()

    inventory = get_inventory()

    product = st.selectbox("Product", inventory["product"])
    quantity = st.number_input("Quantity", 1, 20, 1)

    if st.button("Add to Cart"):

        row = inventory[inventory["product"] == product].iloc[0]

        st.session_state.cart.append({
            "product": product,
            "quantity": quantity,
            "price": row["price"],
            "cost": row["cost"],
            "total": row["price"] * quantity,
            "cogs": row["cost"] * quantity
        })

    if st.session_state.cart:

        df = pd.DataFrame(st.session_state.cart)
        st.subheader("Cart")
        st.dataframe(df)

        subtotal = df["total"].sum()
        tax = subtotal * 0.07
        total = subtotal + tax
        total_cogs = df["cogs"].sum()

        st.write(f"Subtotal: ${round(subtotal,2)}")
        st.write(f"Tax (7%): ${round(tax,2)}")
        st.write(f"Total: ${round(total,2)}")

        payment = st.selectbox("Payment Type", ["Cash", "Card"])

        if st.button("Complete Sale"):

            for item in st.session_state.cart:
                update_inventory(item["product"], item["quantity"])

            post_sale_to_gl(
                entity_id="CAFE",
                total=total,
                tax=tax,
                revenue=subtotal,
                cogs=total_cogs,
                payment_type=payment
            )

            st.session_state.daily_sales.append({
                "time": datetime.now(),
                "total": total
            })

            st.success("Sale Completed")
            st.session_state.cart = []
            st.rerun()


# --------------------------------------------------
# Z REPORT
# --------------------------------------------------

def z_report():

    st.subheader("End of Day Report")

    if st.session_state.daily_sales:

        df = pd.DataFrame(st.session_state.daily_sales)

        total_sales = df["total"].sum()

        st.write(f"Total Sales Today: ${round(total_sales,2)}")

        st.download_button(
            "Download Z Report",
            df.to_csv(index=False),
            file_name="z_report.csv"
        )

    else:
        st.info("No sales today.")


# --------------------------------------------------
# MAIN RENDER
# --------------------------------------------------

def render():

    init_pos()

    if not st.session_state.logged_in:
        login()
    else:
        tabs = st.tabs(["POS Terminal", "End of Day"])

        with tabs[0]:
            pos_screen()

        with tabs[1]:
            z_report()
