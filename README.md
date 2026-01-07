# margin-estimator
Calculate estimated margin requirements for equities options, based on CBOE margining.

> [!NOTE]
> Box spreads and some complex multi-legged positions may be calculated too conservatively.

## Installation

```console
$ pip install margin_estimator
```

## Usage

Simply pass an arbitrary list of legs to the `calculate_margin` function along with an `Underlying` object containing information on the underlying, and you'll get back margin requirement estimates for cash and margin accounts!

```python
from datetime import date
from decimal import Decimal
from margin_estimator import (
    ETFType,
    Option,
    OptionType,
    Underlying,
    calculate_margin,
)

# a SPY iron condor
# make sure to pass `ETFType.BROAD` for broad-based indices
underlying = Underlying(price=Decimal("587.88"), etf_type=ETFType.BROAD)
expiration = date(2024, 12, 20)
long_put = Option(
    expiration=expiration,
    price=Decimal("4.78"),
    quantity=1,
    strike=Decimal(567),
    type=OptionType.PUT,
)
short_put = Option(
    expiration=expiration,
    price=Decimal("5.61"),
    quantity=-1,
    strike=Decimal(572),
    type=OptionType.PUT,
)
short_call = Option(
    expiration=expiration,
    price=Decimal("5.23"),
    quantity=-1,
    strike=Decimal(602),
    type=OptionType.CALL,
)
long_call = Option(
    expiration=expiration,
    price=Decimal("3.68"),
    quantity=1,
    strike=Decimal(607),
    type=OptionType.CALL,
)
margin = calculate_margin(
    [long_put, short_put, long_call, short_call], underlying
)
print(margin)
```

```python
>>> cash_requirement=Decimal('262.00') margin_requirement=Decimal('262.00')
```

For normal equities you can omit the `etf_type` parameter:

```python
# a short F put
underlying = Underlying(price=Decimal("11.03"))
expiration = date(2024, 12, 20)
put = Option(
    expiration=expiration,
    price=Decimal("0.45"),
    quantity=-1,
    strike=Decimal(11),
    type=OptionType.PUT,
)
margin = calculate_margin([put], underlying)
print(margin)
```

```python
>>> cash_requirement=Decimal('1055.00') margin_requirement=Decimal('263.00')
```

And for leveraged products, you'll need to pass in the `leverage_factor`:

```python
# a naked TQQQ call
underlying = Underlying(
    price=Decimal("77.35"),
    etf_type=ETFType.BROAD,
    leverage_factor=Decimal(3),
)
expiration = date(2024, 12, 20)
call = Option(
    expiration=expiration,
    price=Decimal("4.45"),
    quantity=-1,
    strike=Decimal(80),
    type=OptionType.CALL,
)
margin = calculate_margin([call], underlying)
print(margin)
```

```python
>>> cash_requirement=Decimal('7555.00') margin_requirement=Decimal('3661.00')
```

Please note that all numbers are baseline minimums from CBOE guidelines and individual broker margins will likely vary significantly.
