import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
from collections import defaultdict

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

st.set_page_config(layout="wide", page_title="LedgerOne Café ERP")
st.title("LedgerOne Café ERP System")

DB_PATH = "ledger.db"

# -------------------------------------------------
# DATABASE
# -------------------------------------------------

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def initialize_db():
    conn = get_conn()
    c = conn.cursor()

    # Inventory
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product TEXT PRIMARY KEY,
            category TEXT,
            subcategory TEXT,
            price REAL,
            cost REAL,
            stock INTEGER
        )
    """)

    # Journals
    c.execute("""
        CREATE TABLE IF NOT EXISTS journals (
            entity TEXT,
            entry_date TEXT,
            debit TEXT,
            credit TEXT,
            amount REAL
        )
    """)

    conn.commit()
    conn.close()

initialize_db()

# -------------------------------------------------
# SEED INVENTORY
# -------------------------------------------------

def seed_inventory():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone()[0] == 0:
        products = [
            ("Espresso","Beverage","Hot",3,1,100),
            ("Latte","Beverage","Hot",4.5,1.5,100),
            ("Iced Coffee","Beverage","Cold",4,1.2,100),
            ("Croissant","Pastry","Bakery",3.5,1,50),
            ("Muffin","Pastry","Bakery",3,0.9,50)
        ]
        c.executemany("INSERT INTO inventory VALUES (?,?,?,?,?,?)", products)

    conn.commit()
    conn.close()

seed_inventory()

# -------------------------------------------------
# AUTH
# -------------------------------------------------

USERS = {
    "admin":"Owner",
    "manager":"Manager",
    "cashier":"Cashier"
}

def authenticate(user, pw):
    return USERS.get(user)

# -------------------------------------------------
# INVENTORY
# -------------------------------------------------

def get_inventory():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()
    return df

def update_stock(product, qty):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE inventory SET stock = stock - ? WHERE product = ?", (qty,product))
    conn.commit()
    conn.close()

# -------------------------------------------------
# GL POSTING
# -------------------------------------------------

def post_sale(entity, revenue, tax, cogs, payment):

    conn = get_conn()
    c = conn.cursor()

    today = str(date.today())
    cash_acc = "100000001" if payment=="Cash" else "100000002"

    entries = [
        (entity,today,cash_acc,"400000001",revenue),
        (entity,today,cash_acc,"200000001",tax),
        (entity,today,"500000001","100000003",cogs)
    ]

    c.executemany("INSERT INTO journals VALUES (?,?,?,?,?)", entries)

    conn.commit()
    conn.close()

def load_journals():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM journals", conn)
    conn.close()
    return df

# -------------------------------------------------
# REPORTING
# -------------------------------------------------

def trial_balance(df, entity):
    tb = defaultdict(float)
    for _,row in df[df["entity"]==entity].iterrows():
        tb[row["debit"]] += row["amount"]
        tb[row["credit"]] -= row["amount"]
    return pd.DataFrame(tb.items(), columns=["Account","Balance"])

def financials(df, entity):
    tb = trial_balance(df,entity)
    tb["Prefix"] = tb["Account"].str[0]
    income = tb[tb["Prefix"].isin(["4","5"])]
    balance = tb[~tb["Prefix"].isin(["4","5"])]
    return income[["Account","Balance"]], balance[["Account","Balance"]]

def sales_tax_report(df,entity):
    return df[(df["entity"]==entity) & (df["credit"]=="200000001")]["amount"].sum()

def inventory_value():
    inv = get_inventory()
    inv["Value"] = inv["stock"] * inv["cost"]
    return inv[["product","stock","cost","Value"]]

def daily_pnl(df,entity):
    rev = df[(df["entity"]==entity) & (df["credit"]=="400000001")]["amount"].sum()
    cogs = df[(df["entity"]==entity) & (df["debit"]=="500000001")]["amount"].sum()
    return rev,cogs,rev-cogs

# -------------------------------------------------
# SESSION
# -------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if "cart" not in st.session_state:
    st.session_state.cart=[]

# -------------------------------------------------
# LOGIN
# -------------------------------------------------

if not st.session_state.logged_in:

    st.header("Login")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        role = authenticate(user,pw)
        if role:
            st.session_state.logged_in=True
            st.session_state.role=role
            st.session_state.user=user
            st.rerun()
        else:
            st.error("Invalid login")

else:

    st.sidebar.write(f"User: {st.session_state.user}")
    entity = st.sidebar.selectbox("Store",
        ["CAFE","CAFE_DOWNTOWN","CAFE_AIRPORT"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in=False
        st.session_state.cart=[]
        st.rerun()

    tabs = st.tabs([
        "Store Terminal",
        "General Ledger",
        "Trial Balance",
        "Income Statement",
        "Balance Sheet",
        "Inventory Valuation",
        "Sales Tax",
        "Daily P&L"
    ])

    # -------------------------------------------------
    # STORE
    # -------------------------------------------------

    with tabs[0]:

        inv = get_inventory()
        col1,col2 = st.columns([2,1])

        with col1:

            for _,row in inv.iterrows():

                colA,colB = st.columns([3,1])

                with colA:
                    st.write(f"**{row['product']}** ${row['price']}")
                    st.caption(f"Stock {row['stock']}")

                with colB:
                    qty = st.number_input(
                        "",1,row["stock"],1,
                        key=f"qty_{row['product']}"
                    )
                    if st.button("Add",key=f"add_{row['product']}"):
                        st.session_state.cart.append({
                            "product":row["product"],
                            "price":row["price"],
                            "qty":qty,
                            "total":row["price"]*qty,
                            "cogs":row["cost"]*qty
                        })

        with col2:

            if st.session_state.cart:

                df = pd.DataFrame(st.session_state.cart)
                st.dataframe(df[["product","qty","price","total"]])

                subtotal = df["total"].sum()
                tax = round(subtotal*0.07,2)
                total = subtotal+tax
                cogs = df["cogs"].sum()

                st.write("Subtotal:",subtotal)
                st.write("Tax:",tax)
                st.write("Total:",total)

                pay = st.selectbox("Payment",["Cash","Card"])

                if st.button("Checkout"):

                    for item in st.session_state.cart:
                        update_stock(item["product"],item["qty"])

                    post_sale(entity,subtotal,tax,cogs,pay)

                    st.session_state.cart=[]
                    st.success("Sale Completed")
                    st.rerun()

    # -------------------------------------------------
    # REPORTING TABS
    # -------------------------------------------------

    journals = load_journals()

    with tabs[1]:
        st.dataframe(journals[journals["entity"]==entity])

    with tabs[2]:
        st.dataframe(trial_balance(journals,entity))

    with tabs[3]:
        income,_ = financials(journals,entity)
        st.dataframe(income)

    with tabs[4]:
        _,balance = financials(journals,entity)
        st.dataframe(balance)

    with tabs[5]:
        st.dataframe(inventory_value())

    with tabs[6]:
        st.write("Sales Tax Payable:",
                 sales_tax_report(journals,entity))

    with tabs[7]:
        rev,cogs,profit = daily_pnl(journals,entity)
        st.write("Revenue:",rev)
        st.write("COGS:",cogs)
        st.write("Gross Profit:",profit)
