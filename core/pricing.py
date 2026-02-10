def dirty_price(clean_price, accrued_interest):
    return round(clean_price + accrued_interest, 2)

def clean_price(dirty_price, accrued_interest):
    return round(dirty_price - accrued_interest, 2)
