import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DB = "data/ledger.db"

# -------------------------------------------------
# DB CONNECTION
# -------------------------------------------------

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

# -------------------------------------------------
# INITIALIZE DATABASE
# -------------------------------------------------

def initialize_db():

    conn = get_conn()
    c = conn.cursor()

    # Inventory
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product TEXT PRIMARY KEY,
            category TEXT,
            subcategory TEXT,
            description TEXT,
            price REAL,
            cost REAL,
            stock INTEGER
        )
    """)

    # General Ledger
    c.execute("""
        CREATE TABLE IF NOT EXISTS gl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            account TEXT,
            debit REAL,
            credit REAL,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()

# -------------------------------------------------
# SEED INVENTORY
# -------------------------------------------------

def seed_inventory():

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone()[0] == 0:

        products = [
            ("Espresso","Beverage","Hot","Strong black coffee",3,1,100),
            ("Latte","Beverage","Hot","Milk-based espresso drink",4.5,1.5,100),
            ("Iced Coffee","Beverage","Cold","Chilled brewed coffee",4,1.2,100),
            ("Croissant","Pastry","Bakery","Buttery pastry",3.5,1,50),
            ("Muffin","Pastry","Bakery","Fresh baked muffin",3,0.9,50)
        ]

        c.executemany("INSERT INTO inventory VALUES (?,?,?,?,?,?,?)", products)

    conn.commit()
    conn.close()

# -------------------------------------------------
# AUTH
# -------------------------------------------------

def authenticate(user, pwd):

    users = {
        "admin":"Owner",
        "manager":"Manager",
        "cashier":"Cashier"
    }

    return users.get(user)

# -------------------------------------------------
# GL POSTING
# -------------------------------------------------

def post_sale(total, tax, revenue, cogs, payment):

    conn = get_conn()
    c = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cash_account = "Cash" if payment=="Cash" else "Card Receivable"

    entries = [
        (date, cash_account, total, 0, "Sale"),
        (date, "Sales Revenue", 0, revenue, "Sale"),
        (date, "Sales Tax Payable", 0, tax, "Tax"),
        (date, "Cost of Goods Sold", cogs, 0, "COGS"),
        (date, "Inventory", 0, cogs, "Inventory Reduction")
    ]

    c.executemany("""
        INSERT INTO gl (date,account,debit,credit,description)
        VALUES (?,?,?,?,?)
    """, entries)

    conn.commit()
    conn.close()

# -------------------------------------------------
# LOGIN
# -------------------------------------------------

def login():

    st.title("☕ LedgerOne Café ERP")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        role = authenticate(user,pwd)

        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid credentials")

# -------------------------------------------------
# STORE POS
# -------------------------------------------------

def store_terminal():

    conn = get_conn()
    inventory = pd.read_sql("SELECT * FROM inventory", conn)
    conn.close()

    if inventory.empty:
        st.warning("Inventory not available.")
        return

    col1, col2 = st.columns([2,1])

    # LEFT - PRODUCTS
    with col1:

        st.subheader("Products")

        category = st.selectbox("Category", inventory["category"].unique())
        sub = st.selectbox("Subcategory",
                           inventory[inventory["category"]==category]["subcategory"].unique())

        filtered = inventory[
            (inventory["category"]==category) &
            (inventory["subcategory"]==sub)
        ]

        for _, row in filtered.iterrows():

            qty = st.number_input(
                f"Qty - {row['product']}",
                min_value=1,
                value=1,
                key=row['product']
            )

            if st.button(f"Add {row['product']} (${row['price']})",
                         key=row['product']+"_btn"):

                st.session_state.cart.append({
                    "product":row["product"],
                    "price":row["price"],
                    "quantity":qty,
                    "total":row["price"]*qty,
                    "cogs":row["cost"]*qty
                })

                st.rerun()

    # RIGHT - CART
    with col2:

        st.subheader("Cart")

        if st.session_state.cart:

            df = pd.DataFrame(st.session_state.cart)

            display_df = df[["product","price","quantity","total"]]
            st.dataframe(display_df)

            subtotal = df["total"].sum()
            tax = subtotal * 0.07
            total = subtotal + tax
            cogs = df["cogs"].sum()

            st.write(f"Subtotal: ${round(subtotal,2)}")
            st.write(f"Tax: ${round(tax,2)}")
            st.write(f"Total: ${round(total,2)}")

            payment = st.selectbox("Payment",["Cash","Card"])

            if st.button("Checkout"):

                conn = get_conn()
                c = conn.cursor()

                for item in st.session_state.cart:
                    c.execute("""
                        UPDATE inventory
                        SET stock = stock - ?
                        WHERE product=?
                    """,(item["quantity"],item["product"]))

                conn.commit()
                conn.close()

                post_sale(total,tax,subtotal,cogs,payment)

                st.success("Sale Completed")
                st.session_state.cart=[]
                st.rerun()

        else:
            st.info("Cart Empty")

# -------------------------------------------------
# ADMIN INVENTORY
# -------------------------------------------------

def admin_inventory():

    if st.session_state.role not in ["Owner","Manager"]:
        st.warning("Admin access only")
        return

    st.subheader("Add / Update Product")

    product = st.text_input("Product Name")
    category = st.selectbox("Category",["Beverage","Pastry","Food","Merch"])
    sub = st.selectbox("Subcategory",["Hot","Cold","Bakery","Snack","Retail"])
    desc = st.text_area("Description")
    qty = st.number_input("Quantity",0)
    cost = st.number_input("Cost",0.0)
    price = st.number_input("Price",0.0)

    if st.button("Save Product"):

        conn = get_conn()
        c = conn.cursor()

        c.execute("SELECT * FROM inventory WHERE product=?",(product,))
        exists = c.fetchone()

        if exists:
            c.execute("UPDATE inventory SET stock=stock+? WHERE product=?",
                      (qty,product))
            st.success("Stock Updated")
        else:
            c.execute("""
                INSERT INTO inventory VALUES (?,?,?,?,?,?,?)
            """,(product,category,sub,desc,price,cost,qty))
            st.success("Product Added")

        conn.commit()
        conn.close()
        st.rerun()

    conn = get_conn()
    inv = pd.read_sql("SELECT * FROM inventory",conn)
    conn.close()
    st.dataframe(inv)

# -------------------------------------------------
# GL REPORTS
# -------------------------------------------------

def general_ledger():

    conn = get_conn()
    gl = pd.read_sql("SELECT * FROM gl",conn)
    conn.close()
    st.dataframe(gl)

def trial_balance():

    conn = get_conn()
    gl = pd.read_sql("SELECT account, SUM(debit) debit, SUM(credit) credit FROM gl GROUP BY account",conn)
    conn.close()

    gl["balance"] = gl["debit"] - gl["credit"]
    st.dataframe(gl)

def income_statement():

    conn = get_conn()
    gl = pd.read_sql("SELECT account,SUM(debit) debit,SUM(credit) credit FROM gl GROUP BY account",conn)
    conn.close()

    revenue = gl[gl["account"]=="Sales Revenue"]["credit"].sum()
    cogs = gl[gl["account"]=="Cost of Goods Sold"]["debit"].sum()

    st.write("Revenue:",revenue)
    st.write("COGS:",cogs)
    st.write("Net Income:",revenue-cogs)

# -------------------------------------------------
# MAIN RENDER
# -------------------------------------------------

def render():

    initialize_db()
    seed_inventory()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in=False

    if "cart" not in st.session_state:
        st.session_state.cart=[]

    if not st.session_state.logged_in:
        login()
        return

    tabs = st.tabs([
        "Store Terminal",
        "Admin Inventory",
        "General Ledger",
        "Trial Balance",
        "Income Statement"
    ])

    with tabs[0]:
        store_terminal()

    with tabs[1]:
        admin_inventory()

    with tabs[2]:
        general_ledger()

    with tabs[3]:
        trial_balance()

    with tabs[4]:
        income_statement()
