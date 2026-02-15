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

    if inventory.empty:
        st.warning("No products available.")
        return

    col_products, col_cart = st.columns([2, 1])

    # --------------------------------------------------
    # LEFT SIDE — PRODUCTS
    # --------------------------------------------------
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

            stock_level = row["stock"]

            col_item, col_qty = st.columns([3, 1])

            with col_item:
                st.write(f"**{row['product']}**  —  ${row['price']}")

                if stock_level <= 5:
                    st.caption(f"⚠ Low stock: {stock_level}")
                else:
                    st.caption(f"In stock: {stock_level}")

            with col_qty:

                quantity = st.number_input(
                    "",
                    min_value=1,
                    max_value=stock_level if stock_level > 0 else 1,
                    value=1,
                    key=f"qty_{row['product']}"
                )

                if st.button("Add", key=f"add_{row['product']}"):

                    if stock_level < quantity:
                        st.error("Not enough stock.")
                    else:

                        st.session_state.cart.append({
                            "product": row["product"],
                            "price": row["price"],
                            "quantity": quantity,
                            "total": row["price"] * quantity,
                            "cogs": row["cost"] * quantity  # hidden internally
                        })

                        st.success(f"{row['product']} added")

    # --------------------------------------------------
    # RIGHT SIDE — CART
    # --------------------------------------------------
    with col_cart:

        st.subheader("Cart")

        if not st.session_state.cart:
            st.info("Cart empty.")
            return

        df = pd.DataFrame(st.session_state.cart)

        # Only show customer-facing columns
        display_df = df[["product", "quantity", "price", "total"]]

        st.dataframe(display_df, use_container_width=True)

        subtotal = df["total"].sum()
        tax = round(subtotal * 0.07, 2)
        total = round(subtotal + tax, 2)
        total_cogs = df["cogs"].sum()

        st.markdown("---")
        st.write(f"Subtotal: ${subtotal}")
        st.write(f"Sales Tax (7%): ${tax}")
        st.write(f"**Total: ${total}**")

        payment = st.selectbox("Payment Type", ["Cash", "Card"])

        if st.button("Checkout"):

            # Stock validation (double check)
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

            st.session_state.daily_sales.append({
                "time": datetime.now(),
                "total": total
            })

            st.success("Sale Completed")
            st.session_state.cart = []
            st.rerun()

# --------------------------------------------------
# MAIN
# --------------------------------------------------

def render():

    init_pos()

    if not st.session_state.cafe_logged_in:
        login()
    else:
        pos_screen()
