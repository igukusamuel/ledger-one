def accrual_cash_recon(journals):
    accrual = sum(
        j.debit - j.credit
        for j in journals
        if j.account == "Interest Receivable"
    )

    cash = sum(
        j.debit - j.credit
        for j in journals
        if j.account == "Cash"
    )

    return {
        "Accrued Interest Balance": round(accrual, 2),
        "Cash Received": round(cash, 2),
        "Difference": round(accrual - cash, 2)
    }
