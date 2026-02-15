import streamlit as st
import pandas as pd
from core.models import BondTrade

import uuid
import streamlit as st
from datetime import date


def init_trade_capture():
    if "trades" not in st.session_state:
        st.session_state.trades = []

def render():
    init_trade_capture()
    st.header("Trade Capture")
    
    with st.form("bond_trade"):
    trade_date = st.date_input("Trade Date", value=date.today())
    maturity_date = st.date_input("Maturity Date")
    face_value = st.number_input("Face Value", min_value=0.0, value=100000.0)
    coupon_rate = st.number_input("Coupon Rate (%)", min_value=0.0, value=5.0)
    frequency = st.selectbox("Coupon Frequency", [1, 2, 4], index=1)

    submitted = st.form_submit_button("Capture Trade")

    if submitted:
        trade_id = str(uuid.uuid4())

        coupon_amount = face_value * coupon_rate / 100 / frequency

        trade = {
            "trade_id": trade_id,
            "trade_date": trade_date,
            "maturity_date": maturity_date,
            "face_value": face_value,
            "coupon_rate": coupon_rate,
            "frequency": frequency,
            "coupon_amount": coupon_amount,
            "last_coupon_date": trade_date,
            "status": "OPEN"
        }

        st.session_state.trades.append(trade)

        # 🔗 CRITICAL LINK TO SUBLEDGER
        st.session_state["active_trade_id"] = trade_id
        st.session_state["last_coupon_date"] = trade_date
        st.session_state["coupon_amount"] = coupon_amount

        st.success("Trade captured and linked to subledger.")

