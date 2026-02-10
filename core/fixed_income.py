from dateutil.relativedelta import relativedelta

def generate_coupon_schedule(
    trade_date,
    maturity_date,
    face_value,
    coupon_rate,
    frequency=2,  # default semi-annual
):
    schedule = []
    months = 12 // frequency
    coupon_amount = face_value * coupon_rate / 100 / frequency

    pay_date = maturity_date
    while pay_date > trade_date:
        schedule.append({
            "date": pay_date,
            "type": "Coupon",
            "amount": round(coupon_amount, 2)
        })
        pay_date -= relativedelta(months=months)

    schedule.append({
        "date": maturity_date,
        "type": "Principal",
        "amount": round(face_value, 2)
    })

    return sorted(schedule, key=lambda x: x["date"])
