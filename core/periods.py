from datetime import date

def is_period_open(valuation_date, closed_periods):
    return valuation_date not in closed_periods
