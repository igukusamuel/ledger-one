from datetime import date

def accrued_interest(
    last_coupon_date: date,
    valuation_date: date,
    coupon_amount: float,
    day_count: int = 360,
):
    days = (valuation_date - last_coupon_date).days
    return round(coupon_amount * days / day_count, 2)
