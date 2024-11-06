from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class ETFType(StrEnum):
    BROAD = "broad-based"
    NARROW = "narrow-based"
    VOLATILITY = "volatility"


class OptionType(StrEnum):
    CALL = "C"
    PUT = "P"


class Option(BaseModel):
    expiration: date
    price: Decimal
    quantity: int
    strike: Decimal
    type: OptionType


class MarginRequirements(BaseModel):
    cash_requirement: Decimal
    margin_requirement: Decimal

    def __add__(self, other: "MarginRequirements"):
        return MarginRequirements(
            cash_requirement=self.cash_requirement + other.cash_requirement,
            margin_requirement=self.margin_requirement + other.margin_requirement,
        )


class Underlying(BaseModel):
    etf_type: ETFType | None = None
    leverage_factor: Decimal = Decimal(1)
    price: Decimal
