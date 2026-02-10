import streamlit as st
import pandas as pd
from dataclasses import dataclass, asdict
from datetime import date
import json
import io

st.set_page_config(page_title="LedgerOne", layout="wide")

# =====================================================
# DATA MODELS
# =====================================================

@dataclass
class BondTrade:
    trade_id: str
    trade_date: date
    maturity_date: date
    face_value: float
    coupon_rate: float
    price: float
    direction: str


@dataclass
class JournalEntry:
    account: str
    debit: float
    credit: float
    memo: str


@dataclass
class TaxpayerInfo:
    first_name: str
    last_name: str
    country_of_residence: str
    filing_status: str


@dataclass
class Income1040:
    wages: float = 0.0
    interest: float = 0.0
    dividends: float = 0.0
    capital_gains: float = 0.0


@dataclass
class Income1040NR:
    wages_us: float = 0.0
    business_income_eci: float = 0.0
    capital_gains_us: float = 0.0
    fdap_income_us: float = 0.0


@dataclass
class Payments:
    withholding: float = 0.0
    estimated_payments: float = 0.0


@dataclass
class TaxReturn1040:
    taxpayer: TaxpayerInfo
    income: Income1040
    payments: Payments

    def agi(self):
        return sum(asdict(self.income).values())


@dataclass
class TaxReturn1040NR:
    taxpayer: TaxpayerInfo
    income: Income1040NR
    payments: Payments

    def agi(self):
        return (
            self.income.wages_us
            + self.income.business_income_eci
            + self.income.capital_gains_us
        )

# ====================================
