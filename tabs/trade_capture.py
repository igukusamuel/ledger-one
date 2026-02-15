import streamlit as st
from core.persistence import save_trade, load_trades


def render():

    st.header("Trade Capture System")

    entity_id = st.text_input("Entity ID", value="ENTITY_001")

    trade_date = st.date_input("Trade Date")
    instrument_type = st.selectbox("Instrument Type", ["Bond"])
    face_value = st.number_input("Face Value", min_value=0.0)
    coupon_rate = st.number_input("Coupon Rate (%)", min_value=0.0)
    maturity_date = st.date_input("Maturity Date")
    price = st.number_input("Price", min_value=0.0)

    if st.button("Save Trade", key="save_trade_btn"):

        save_trade(
            entity_id,
            str(trade_date),
            instrument_type,
            face_value,
            coupon_rate,
            str(maturity_date),
            price
        )

        st.success("Trade Saved Successfully")

    st.subheader("Saved Trades")

    trades = load_trades()

    if trades:
        st.dataframe(trades)
    else:
        st.info("No trades captured yet.")
