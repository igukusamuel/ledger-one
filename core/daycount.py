from datetime import date

def day_count_fraction(start: date, end: date, convention="ACT/360"):
    days = (end - start).days

    if convention == "ACT/360":
        return days / 360
    if convention == "ACT/365":
        return days / 365
    if convention == "30/360":
        return (
            (end.year - start.year) * 360 +
            (end.month - start.month) * 30 +
            (end.day - start.day)
        ) / 360

    raise ValueError("Unsupported day count convention")
