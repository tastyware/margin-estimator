import re
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ETFType(StrEnum):
    BROAD = "broad-based"
    NARROW = "narrow-based"
    VOLATILITY = "volatility"


class OptionType(StrEnum):
    CALL = "C"
    PUT = "P"


class Option(BaseModel):
    model_config = ConfigDict(frozen=True)

    expiration: date
    price: Decimal
    quantity: int
    strike: Decimal
    type: OptionType

    def __lt__(self, other: "Option"):
        return (self.expiration, self.strike, self.type.value) < (
            other.expiration,
            other.strike,
            other.type.value,
        )

    @classmethod
    def from_occ(cls, symbol: str, price: Decimal, quantity: int) -> "Option":
        match = re.match(r"(\d{6})([CP])(\d{5})(\d{3})", symbol[6:])
        assert match
        exp = datetime.strptime(match.group(1), "%y%m%d").date()
        option_type = match.group(2)
        strike = int(match.group(3)) + Decimal(match.group(4)) / 1000
        return cls(
            expiration=exp,
            price=price,
            quantity=quantity,
            strike=strike,
            type=OptionType(option_type),
        )

    @classmethod
    def from_dxfeed(cls, symbol: str, price: Decimal, quantity: int) -> "Option":
        match = re.match(r"\.([A-Z]+)(\d{6})([CP])(\d+(\.\d+)?)", symbol)
        assert match
        exp = datetime.strptime(match.group(2), "%y%m%d").date()
        option_type = match.group(3)
        strike = Decimal(match.group(4))
        return cls(
            expiration=exp,
            price=price,
            quantity=quantity,
            strike=strike,
            type=OptionType(option_type),
        )


class MarginRequirements(BaseModel):
    cash_requirement: Decimal
    margin_requirement: Decimal

    def __add__(self, other: "MarginRequirements"):
        return MarginRequirements(
            cash_requirement=self.cash_requirement + other.cash_requirement,
            margin_requirement=self.margin_requirement + other.margin_requirement,
        )

    def __eq__(self, other):
        return (
            self.cash_requirement == other.cash_requirement
            and self.margin_requirement == other.margin_requirement
        )


class Underlying(BaseModel):
    etf_type: ETFType | None = None
    leverage_factor: Decimal = Decimal(1)
    price: Decimal
