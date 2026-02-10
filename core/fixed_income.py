from datetime import date
from dateutil.relativedelta import relativedelta

def generate_coupon_schedule(
    trade_date: date,
    maturity_date: date,
    face_value: float,
    coupon_rate: float,
    frequency: int = 1,  # annual
):
    """
    Returns list of (date, amount)
    """
    schedule = []
    coupon_amount = face_value * coupon_rate / 100 / frequency

    pay_date = maturity_date
    while pay_date > trade_date:
        schedule.append(
            {
                "date": pay_date,
                "type": "Coupon",
                "amount": round(coupon_amount, 2),
            }
        )
        pay_date = pay_date - relativedelta(months=12 // frequency)

    # Principal at maturity
    schedule.append(
        {
            "date": maturity_date,
            "type": "Principal",
            "amount": round(face_value, 2),
        }
    )

    return sorted(schedule, key=lambda x: x["date"])
