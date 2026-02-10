def interest_to_tax(journal_entries):
    """
    Extracts interest income for tax reporting
    """
    interest = 0.0
    for j in journal_entries:
        if "Interest Income" in j.account:
            interest += j.credit - j.debit
    return round(interest, 2)
