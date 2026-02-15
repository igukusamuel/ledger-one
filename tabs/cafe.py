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

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Table
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os


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

    if "cafe_receipt_ready" not in st.session_state:
        st.session_state.cafe_receipt_ready = None


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
        ["POS Terminal", "Analytics", "End of Day", "Inventory Management"]
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
    elif menu == "Analytics":
        analytics_dashboard()
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
        st.warning("No products available.")
        return

    col1, col2 = st.columns([2, 1])

    # -----------------------
    # PRODUCT PANEL
    # -----------------------
    with col1:

        st.subheader("Products")

        categories = inventory["category"].unique()
        selected_category = st.selectbox("Category", categories)

        filtered_cat = inventory[inventory["category"] == selected_category]

        for _, row in filtered_cat.iterrows():

            if st.button(
                f"{row['product']} (${row['price']}) | Stock: {row['stock']}",
                key=row['product']
            ):

                if row["stock"] <= 0:
                    st.warning("Out of stock")
                else:
                    st.session_state.cafe_cart.append({
                        "product": row["product"],
                        "price": row["price"],
                        "cost": row["cost"],
                        "quantity": 1
                    })
                    st.rerun()

    # -----------------------
    # CART PANEL
    # -----------------------
    with col2:

        st.subheader("Cart")

        if st.session_state.cafe_cart:

            for i, item in enumerate(st.session_state.cafe_cart):

                colA, colB, colC = st.columns([2, 1, 1])

                colA.write(item["product"])

                new_qty = colB.number_input(
                    "Qty",
                    min_value=1,
                    value=item["quantity"],
                    key=f"qty_{i}"
                )

                st.session_state.cafe_cart[i]["quantity"] = new_qty

                if colC.button("❌", key=f"remove_{i}"):
                    st.session_state.cafe_cart.pop(i)
                    st.rerun()

            df = pd.DataFrame(st.session_state.cafe_cart)
            df["total"] = df["price"] * df["quantity"]
            df["cogs"] = df["cost"] * df["quantity"]

            subtotal = df["total"].sum()
            tax = subtotal * 0.07
            total = subtotal + tax
            total_cogs = df["cogs"].sum()
            margin = subtotal - total_cogs

            st.markdown("---")
            st.write(f"Subtotal: ${round(subtotal,2)}")
            st.write(f"Tax: ${round(tax,2)}")
            st.write(f"Total: ${round(total,2)}")
            st.write(f"Margin: ${round(margin,2)}")

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
                    "revenue": subtotal,
                    "cogs": total_cogs,
                    "margin": margin
                })

                generate_receipt(df, subtotal, tax, total)

                st.session_state.cafe_cart = []
                st.success("Sale Completed")
                st.rerun()

        else:
            st.info("Cart empty")


# --------------------------------------------------
# ANALYTICS DASHBOARD
# --------------------------------------------------

def analytics_dashboard():

    st.subheader("Sales Analytics")

    if not st.session_state.cafe_daily_sales:
        st.info("No sales yet.")
        return

    df = pd.DataFrame(st.session_state.cafe_daily_sales)

    total_rev = df["revenue"].sum()
    total_cogs = df["cogs"].sum()
    total_margin = df["margin"].sum()
    margin_pct = total_margin / total_rev if total_rev > 0 else 0

    st.metric("Total Revenue", f"${round(total_rev,2)}")
    st.metric("Total Margin", f"${round(total_margin,2)}")
    st.metric("Margin %", f"{round(margin_pct*100,2)}%")


# --------------------------------------------------
# RECEIPT GENERATOR
# --------------------------------------------------

def generate_receipt(df, subtotal, tax, total):

    os.makedirs("data", exist_ok=True)

    file_path = "data/receipt.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []

    elements.append(Paragraph("LedgerOne Café Receipt", ParagraphStyle(name='Normal')))
    elements.append(Spacer(1, 0.25 * inch))

    table_data = [["Item", "Qty", "Price"]]

    for _, row in df.iterrows():
        table_data.append([
            row["product"],
            row["quantity"],
            f"${row['total']}"
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.25 * inch))

    elements.append(Paragraph(f"Subtotal: ${round(subtotal,2)}", ParagraphStyle(name='Normal')))
    elements.append(Paragraph(f"Tax: ${round(tax,2)}", ParagraphStyle(name='Normal')))
    elements.append(Paragraph(f"Total: ${round(total,2)}", ParagraphStyle(name='Normal')))

    doc.build(elements)

    with open(file_path, "rb") as f:
        st.download_button("Download Receipt", f, file_name="receipt.pdf")


# --------------------------------------------------
# INVENTORY MANAGEMENT
# --------------------------------------------------

def inventory_manager():

    if st.session_state.cafe_role not in ["Owner", "Manager"]:
        st.error("Restricted access.")
        return

    st.subheader("Add Product")

    product = st.text_input("Product Name")
    category = st.text_input("Category")
    subcategory = st.text_input("Subcategory")
    price = st.number_input("Selling Price", min_value=0.0)
    cost = st.number_input("Cost", min_value=0.0)
    stock = st.number_input("Stock", min_value=0)

    if st.button("Save"):
        add_product(product, category, subcategory, price, cost, stock)
        st.success("Saved")
        st.rerun()

    st.markdown("---")
    st.subheader("Inventory")

    inv = get_inventory()
    st.dataframe(inv)

    st.markdown("### Replenish Stock")

    selected = st.selectbox("Product", inv["product"])
    qty = st.number_input("Add Quantity", min_value=1)

    if st.button("Replenish"):
        add_product(
            selected,
            inv[inv["product"]==selected]["category"].values[0],
            inv[inv["product"]==selected]["subcategory"].values[0],
            inv[inv["product"]==selected]["price"].values[0],
            inv[inv["product"]==selected]["cost"].values[0],
            inv[inv["product"]==selected]["stock"].values[0] + qty
        )
        st.success("Stock Updated")
        st.rerun()


# --------------------------------------------------
# END OF DAY
# --------------------------------------------------

def z_report():

    st.subheader("Z Report")

    if not st.session_state.cafe_daily_sales:
        st.info("No sales today.")
        return

    df = pd.DataFrame(st.session_state.cafe_daily_sales)
    total = df["revenue"].sum()

    st.write(f"Total Sales: ${round(total,2)}")
    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        file_name="z_report.csv"
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def render():

    init_cafe()

    if not st.session_state.cafe_logged_in:
        login()
    else:
        store_terminal()
