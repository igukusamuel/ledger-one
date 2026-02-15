import streamlit as st
import pandas as pd
from datetime import datetime
from core.auth import authenticate
from core.inventory import (
    init_inventory,
    get_inventory,
    add_product,
    update_inventory
)
from core.pos_gl import post_sale_to_gl


# --------------------------------------------------
# INIT
# --------------------------------------------------

def init_cafe():

    init_inventory()

    if "cafe_logged_in" not in st.session_state:
        st.session_state.cafe_logged_in = False

    if "cafe_cart" not in st.session_state:
        st.session_state.cafe_cart = []

    if "cafe_daily_sales" not in st.session_state:
        st.session_state.cafe_daily_sales = []


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

def login():

    st.title("☕ LedgerOne Café")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        role = authenticate(username, password)

        if role:
            st.session_state.cafe_logged_in = True
            st.session_state.cafe_role = role
            st.session_state.cafe_username = username
            st.rerun()
        else:
            st.error("Invalid credentials")


# --------------------------------------------------
# STORE TERMINAL
# --------------------------------------------------

def store_terminal():

    st.sidebar.header("Navigation")

    menu = st.sidebar.radio(
        "Menu",
        ["POS Terminal", "End of Day", "Inventory Management"]
    )

    st.sidebar.markdown("---")
    st.sidebar.write(f"User: {st.session_state.cafe_username}")
    st.sidebar.write(f"Role: {st.session_state.cafe_role}")

    if st.sidebar.button("Logout"):
        st.session_state.cafe_logged_in = False
        st.session_state.cafe_cart = []
        st.rerun()

    if menu == "POS Terminal":
        pos_screen()

    elif menu == "End of Day":
        z_report()

    elif menu == "Inventory Management":
        inventory_manager()


# --------------------------------------------------
# POS SCREEN
# --------------------------------------------------

def pos_screen():

    inventory = get_inventory()

    if inventory.empty:
        st.warning("No products available. Add products in Inventory Management.")
        return

    col1, col2 = st.columns([2, 1])

    # LEFT PANEL - PRODUCTS
    with col1:

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
            if st.button(
                f"{row['product']} - ${row['price']}",
                key=f"prod_{row['product']}"
            ):
                st.session_state.cafe_cart.append({
                    "product": row["product"],
                    "price": row["price"],
                    "cost": row["cost"],
                    "quantity": 1,
                    "total": row["price"],
                    "cogs": row["cost"]
                })
                st.rerun()

    # RIGHT PANEL - CART
    with col2:

        st.subheader("Cart")

        if st.session_state.cafe_cart:

            df = pd.DataFrame(st.session_state.cafe_cart)
            st.dataframe(df)

            subtotal = df["total"].sum()
            tax = subtotal * 0.07
            total = subtotal + tax
            total_cogs = df["cogs"].sum()

            st.write(f"Subtotal: ${round(subtotal,2)}")
            st.write(f"Tax (7%): ${round(tax,2)}")
            st.write(f"Total: ${round(total,2)}")

            payment = st.selectbox("Payment Type", ["Cash", "Card"])

            if st.button("Checkout"):

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

                st.session_state.cafe_daily_sales.append({
                    "time": datetime.now(),
                    "total": total
                })

                st.success("Sale Completed")
                st.session_state.cafe_cart = []
                st.rerun()

        else:
            st.info("Cart empty.")


# --------------------------------------------------
# INVENTORY MANAGEMENT
# --------------------------------------------------

def inventory_manager():

    if st.session_state.cafe_role not in ["Owner", "Manager"]:
        st.error("Access restricted to Manager or Owner.")
        return

    st.subheader("Add / Update Product")

    product = st.text_input("Product Name")
    category = st.selectbox("Category", ["Beverage", "Pastry"])
    subcategory = st.selectbox("Subcategory", ["Hot", "Cold", "Bakery"])
    price = st.number_input("Selling Price", min_value=0.0)
    cost = st.number_input("Cost", min_value=0.0)
    stock = st.number_input("Initial Stock", min_value=0)

    if st.button("Save Product"):
        add_product(product, category, subcategory, price, cost, stock)
        st.success("Product Saved")
        st.rerun()

    st.markdown("---")
    st.subheader("Current Inventory")
    st.dataframe(get_inventory())


# --------------------------------------------------
# END OF DAY REPORT
# --------------------------------------------------

def z_report():

    st.subheader("End of Day Report")

    if st.session_state.cafe_daily_sales:

        df = pd.DataFrame(st.session_state.cafe_daily_sales)
        total_sales = df["total"].sum()

        st.write(f"Total Sales: ${round(total_sales,2)}")

        st.download_button(
            "Download Z Report",
            df.to_csv(index=False),
            file_name="z_report.csv"
        )
    else:
        st.info("No sales today.")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def render():

    init_cafe()

    if not st.session_state.cafe_logged_in:
        login()
    else:
        store_terminal()
