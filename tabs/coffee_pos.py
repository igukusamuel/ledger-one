import streamlit as st
import pandas as pd
from datetime import datetime
from core.auth import authenticate
from core.pos_gl import post_sale_to_gl
from core.inventory import get_inventory, update_inventory


# --------------------------------------------------
# INIT
# --------------------------------------------------

def init_pos():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "cart" not in st.session_state:
        st.session_state.cart = []


# --------------------------------------------------
# LOGIN SCREEN
# --------------------------------------------------

def login_screen():

    st.title("☕ LedgerOne Café POS")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        role = authenticate(username, password)

        if role:
            st.session_state.logged_in = True
            st.session_state.user_role = role
            st.session_state.username = username
            st.success(f"Logged in as {role}")
            st.rerun()
        else:
            st.error("Invalid credentials")


# --------------------------------------------------
# POS INTERFACE
# --------------------------------------------------

def pos_interface():

    st.title("☕ Coffee Café POS")

    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    st.sidebar.write(f"Role: {st.session_state.user_role}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.cart = []
        st.rerun()

    inventory = get_inventory()

    product = st.selectbox("Select Product", inventory["Product"])
    quantity = st.number_input("Quantity", min_value=1, value=1)

    if st.button("Add to Cart"):
        price = inventory.loc[inventory["Product"] == product, "Price"].values[0]
        st.session_state.cart.append({
            "Product": product,
            "Quantity": quantity,
            "Price": price,
            "Total": price * quantity
        })

    # CART DISPLAY
    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.subheader("Cart")
        st.dataframe(cart_df)

        subtotal = cart_df["Total"].sum()
        tax = subtotal * 0.07
        total = subtotal + tax

        st.write(f"Subtotal: ${round(subtotal,2)}")
        st.write(f"Tax (7%): ${round(tax,2)}")
        st.write(f"Total: ${round(total,2)}")

        payment_method = st.selectbox("Payment Method", ["Cash", "Card"])

        if st.button("Complete Sale"):

            # Update inventory
            for item in st.session_state.cart:
                update_inventory(item["Product"], item["Quantity"])

            # Post to GL
            post_sale_to_gl(total, tax)

            st.success("Sale Completed")
            st.session_state.cart = []
            st.rerun()


# --------------------------------------------------
# MAIN RENDER
# --------------------------------------------------

def render():

    init_pos()

    if not st.session_state.logged_in:
        login_screen()
    else:
        pos_interface()
