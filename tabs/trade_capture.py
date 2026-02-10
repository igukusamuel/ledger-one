import streamlit as st
import pandas as pd
from core.models import BondTrade

def render():
    st.header("Trade Capture — Plain Vanilla Bond")

    c1, c2 = st.columns(2)

    trade_id = c1.text_input("Trade ID")
    direction = c2.selectbox("Direction", ["Buy", "Sell"])
    trade_date = c1.date_input("Trade Date")
    maturity_date = c2.date_input("Maturity Date")
    face_value = c1.number_input("Face Value", min_value=0.0, step=1000.0)
    coupon = c2.number_input("Coupon Rate (%)", min_value=0.0, step=0.25)
    price = st.number_input("Clean Price (%)", min_value=0.0, step=0.1)

    if st.button("Capture Trade"):
        st.session_state.trades.append(
            BondTrade(
                trade_id,
                trade_date,
                maturity_date,
                face_value,
                coupon,
                price,
                direction,
            )
        )
        st.success("Trade captured")

    if st.session_state.trades:
        st.dataframe(pd.DataFrame([t.__dict__ for t in st.session_state.trades]))
