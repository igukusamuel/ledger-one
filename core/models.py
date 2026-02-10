from dataclasses import dataclass
from datetime import date

# ========= TRADING =========

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


# ========= TAX =========

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
class TradeLifecycle:
    status: str  # OPEN / SOLD / MATURED
    termination_date: date | None = None
    termination_price: float | None = None

