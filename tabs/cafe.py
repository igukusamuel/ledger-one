import streamlit as st
import pandas as pd
from datetime import datetime
from core.auth import authenticate
from core.inventory import init_inventory, get_inventory, add_product, update_inventory
from core.pos_gl import post_sale_to_gl


# --------------------------------------------------
# INIT
# --------------------------------------------------

def init_pos():

    init_inventory()

    if "cafe_logged_in" not in st.session_state:
        st.session_state.cafe_logged_in = False

    if "cafe_cart" not in st.session_state:
        st.session_state.cafe_cart = []

    if "cafe_sales" not in st.session_state:
        st.session_state.cafe_sales = []


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

def login():

    st.title("☕ LedgerOne Café")

    username = st.text_input("Username", key="cafe_user")
    password = st.text_input("Password", type="password", key="cafe_pass")

    if st.button("Login", key="cafe_login_btn"):

        role = authenticate(username, password)

        if role:
            st.session_state.cafe_logged_in = True
            st.session_state.cafe_role = role
            st.session_state.cafe_username = username
            st.rerun()
        else:
            st.error("Invalid credentials")


# --------------------------------------------------
# POS SCREEN
# --------------------------------------------------

def pos_screen():

    inventory = get_inventory()

    if inventory is None or inventory.empty:
        st.warning("Inventory empty.")
        return

    col1, col2 = st.columns([2, 1])

    # LEFT SIDE PRODUCTS
    with col1:

        st.subheader("Products")

        categories = inventory["category"].unique()
        category = st.selectbox("Category", categories, key="cafe_cat")

        subcategories = inventory[inventory["category"] == category]["subcategory"].unique()
        subcategory = st.selectbox("Subcategory", subcategories, key="cafe_subcat")

        filtered = inventory[
            (inventory["category"] == category) &
            (inventory["subcategory"] == subcategory)
        ]

        for _, row in filtered.iterrows():

            if st.button(f"{row['product']} - ${row['price']}", key=f"btn_{row['product']}"):

                st.session_state.cafe_cart.append({
                    "product": row["product"],
                    "price": row["price"],
                    "cost": row["cost"],
                    "quantity": 1
                })

                st.rerun()

    # RIGHT SIDE CART
    with col2:

        st.subheader("Cart")

        if st.session_state.cafe_cart:

            df = pd.DataFrame(st.session_state.cafe_cart)
            df["total"] = df["price"] * df["quantity"]

            st.dataframe(df)

            subtotal = df["total"].sum()
            tax = subtotal * 0.07
            total = subtotal + tax
            total_cogs = (df["cost"] * df["quantity"]).sum()

            st.write(f"Subtotal: ${subtotal:.2f}")
            st.write(f"Tax: ${tax:.2f}")
            st.write(f"Total: ${total:.2f}")

            payment = st.selectbox("Payment", ["Cash", "Card"], key="cafe_payment")

            if st.button("Checkout", key="cafe_checkout"):

                for item in st.session_state.cafe_cart:
                    update_inventory(item["product"], item["quantity"])

                post_sale_to_gl(
                    entity_id="CAFE",
                    total=total,
                    tax=tax,
                    revenue=subtotal,
                    cogs=total_cogs,
                    payment_type=payment
                )

                st.session_state.cafe_sales.append({
                    "time": datetime.now(),
                    "total": total
                })

                st.session_state.cafe_cart = []

                st.success("Sale Completed")
                st.rerun()

        else:
            st.info("Cart empty.")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def render():

    init_pos()

    if not st.session_state.cafe_logged_in:
        login()
    else:
        pos_screen()
