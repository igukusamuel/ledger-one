import streamlit as st
import uuid
from datetime import date


# -----------------------------
# Initialization
# -----------------------------

def init_trade_capture():
    from core.persistence import load_trades
    if "trades" not in st.session_state:
        st.session_state.trades = load_trades()

    if "active_trade_id" not in st.session_state:
        st.session_state.active_trade_id = None

# -----------------------------
# Helpers
# -----------------------------

def calculate_coupon(face_value, coupon_rate, frequency):
    return face_value * coupon_rate / 100 / frequency


def get_active_trade():
    if not st.session_state.active_trade_id:
        return None

    return next(
        (t for t in st.session_state.trades
         if t["trade_id"] == st.session_state.active_trade_id),
        None
    )


# -----------------------------
# Trade Capture UI
# -----------------------------

def render():
    init_trade_capture()

    st.header("Trade Capture System")
    st.subheader("Plain Vanilla Bond")

    with st.form("bond_trade_form"):
        col1, col2 = st.columns(2)

        with col1:
            trade_date = st.date_input("Trade Date", value=date.today())
            maturity_date = st.date_input("Maturity Date")
            face_value = st.number_input(
                "Face Value",
                min_value=0.0,
                value=100000.0,
                step=1000.0
            )

        with col2:
            coupon_rate = st.number_input(
                "Coupon Rate (%)",
                min_value=0.0,
                value=5.0,
                step=0.1
            )

            frequency = st.selectbox(
                "Coupon Frequency",
                options=[1, 2, 4],
                format_func=lambda x: {
                    1: "Annual",
                    2: "Semi-Annual",
                    4: "Quarterly"
                }[x],
                index=1
            )

        submitted = st.form_submit_button("Capture Trade")

        if submitted:
            from core.persistence import save_trades
            if maturity_date <= trade_date:
                st.error("Maturity date must be after trade date.")
            else:
                trade_id = str(uuid.uuid4())
                coupon_amount = calculate_coupon(
                    face_value,
                    coupon_rate,
                    frequency
                )

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
                save_trades(st.session_state.trades)

                # 🔗 Link to Subledger
                st.session_state.active_trade_id = trade_id
                st.session_state.last_coupon_date = trade_date
                st.session_state.coupon_amount = coupon_amount

                st.success("Trade captured and linked to subledger.")


    # -----------------------------
    # Display Existing Trades
    # -----------------------------

    st.subheader("Captured Trades")

    if not st.session_state.trades:
        st.info("No trades captured yet.")
        return

    for trade in st.session_state.trades:
        is_active = (
            trade["trade_id"] == st.session_state.active_trade_id
        )

        with st.expander(
            f"Trade ID: {trade['trade_id'][:8]} "
            f"{'(ACTIVE)' if is_active else ''}"
        ):
            st.write(f"Trade Date: {trade['trade_date']}")
            st.write(f"Maturity Date: {trade['maturity_date']}")
            st.write(f"Face Value: {trade['face_value']}")
            st.write(f"Coupon Rate: {trade['coupon_rate']}%")
            st.write(f"Frequency: {trade['frequency']} per year")
            st.write(f"Coupon Amount: {round(trade['coupon_amount'], 2)}")
            st.write(f"Status: {trade['status']}")

            if not is_active:
                if st.button(
                    "Set as Active",
                    key=f"activate_{trade['trade_id']}"
                ):
                    st.session_state.active_trade_id = trade["trade_id"]
                    st.session_state.last_coupon_date = trade["last_coupon_date"]
                    st.session_state.coupon_amount = trade["coupon_amount"]
                    st.success("Active trade updated.")
