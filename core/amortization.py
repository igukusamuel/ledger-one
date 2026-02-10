def amortize_bond(
    purchase_price: float,
    face_value: float,
    periods: int,
):
    """
    Straight-line amortization (prototype-safe)
    """
    premium_discount = purchase_price - face_value
    amort_per_period = premium_discount / periods

    schedule = []
    carrying_value = purchase_price

    for p in range(1, periods + 1):
        carrying_value -= amort_per_period
        schedule.append(
            {
                "period": p,
                "amortization": round(amort_per_period, 2),
                "carrying_value": round(carrying_value, 2),
            }
        )

    return schedule
