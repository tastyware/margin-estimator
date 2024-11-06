from datetime import date
from decimal import Decimal

from src import Option, OptionType, Underlying, calculate_margin


def test_long_option():
    expiration = date(2024, 12, 20)
    underlying = Underlying(price=128.5)
    call = Option(
        expiration=expiration, price=5, quantity=1, strike=125, type=OptionType.CALL
    )
    margin = calculate_margin([call], underlying)
    assert margin.margin_requirement == Decimal(500)
