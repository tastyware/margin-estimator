import random
from datetime import date, timedelta
from decimal import Decimal

from margin_estimator import (
    ETFType,
    Option,
    OptionType,
    Underlying,
    calculate_margin,
)


def test_long_option():
    underlying = Underlying(price=Decimal("128.5"))
    call = Option(
        expiration=date.today(), price=5, quantity=1, strike=125, type=OptionType.CALL
    )
    margin = calculate_margin([call], underlying)
    assert margin.margin_requirement == Decimal(500)


def test_long_option_index():
    underlying = Underlying(price=Decimal("433.35"), etf_type=ETFType.BROAD)
    put = Option(
        expiration=date.today(),
        price=Decimal("5.5"),
        quantity=1,
        strike=430,
        type=OptionType.PUT,
    )
    margin = calculate_margin([put], underlying)
    assert margin.margin_requirement == Decimal(550)


def test_long_option_18_months():
    underlying = Underlying(price=78)
    call = Option(
        expiration=date.today() + timedelta(days=18 * 30),
        price=12,
        quantity=1,
        strike=80,
        type=OptionType.CALL,
    )
    margin = calculate_margin([call], underlying)
    assert margin.cash_requirement == Decimal(1200)
    assert margin.margin_requirement == Decimal(900)


def test_long_option_20_months():
    underlying = Underlying(price=1290)
    call = Option(
        expiration=date.today() + timedelta(days=20 * 30),
        price=Decimal("16.8"),
        quantity=1,
        strike=1325,
        type=OptionType.CALL,
    )
    margin = calculate_margin([call], underlying)
    assert margin.cash_requirement == Decimal(1260 * 4 / 3)
    assert margin.margin_requirement == Decimal(1260)


def test_short_put():
    underlying = Underlying(price=95)
    put = Option(
        expiration=date.today(), price=2, quantity=-1, strike=80, type=OptionType.PUT
    )
    margin = calculate_margin([put], underlying)
    assert margin.cash_requirement == Decimal(7800)
    assert margin.margin_requirement == Decimal(1000)


def test_short_put_itm():
    underlying = Underlying(price=Decimal("19.5"))
    put = Option(
        expiration=date.today(),
        price=Decimal("1.5"),
        quantity=-1,
        strike=20,
        type=OptionType.PUT,
    )
    margin = calculate_margin([put], underlying)
    assert margin.cash_requirement == Decimal(1850)
    assert margin.margin_requirement == Decimal(540)


def test_short_leveraged():
    underlying = Underlying(price=970, leverage_factor=2)
    put = Option(
        expiration=date.today(), price=3, quantity=-1, strike=725, type=OptionType.PUT
    )
    margin = calculate_margin([put], underlying)
    assert margin.cash_requirement == Decimal(72200)
    assert margin.margin_requirement == Decimal(14800)


def test_short_leveraged_itm():
    underlying = Underlying(price=Decimal("390.7"), leverage_factor=3)
    put = Option(
        expiration=date.today(),
        price=Decimal("15.5"),
        quantity=-1,
        strike=400,
        type=OptionType.PUT,
    )
    margin = calculate_margin([put], underlying)
    assert margin.cash_requirement == Decimal(38450)
    assert margin.margin_requirement == Decimal(24992)


def test_short_broad():
    underlying = Underlying(price=Decimal("445.35"), etf_type=ETFType.BROAD)
    put = Option(
        expiration=date.today(),
        price=Decimal("0.1"),
        quantity=-1,
        strike=410,
        type=OptionType.PUT,
    )
    margin = calculate_margin([put], underlying)
    assert margin.cash_requirement == Decimal(40990)
    assert margin.margin_requirement == Decimal(4110)


def test_short_broad_2():
    underlying = Underlying(price=Decimal("433.35"), etf_type=ETFType.BROAD)
    put = Option(
        expiration=date.today(),
        price=Decimal("7.8"),
        quantity=-1,
        strike=430,
        type=OptionType.PUT,
    )
    margin = calculate_margin([put], underlying)
    assert margin.cash_requirement == Decimal(42220)
    assert margin.margin_requirement == Decimal(6945)


def test_short_broad_itm():
    underlying = Underlying(price=Decimal("43.34"), etf_type=ETFType.BROAD)
    put = Option(
        expiration=date.today() + timedelta(days=24 * 30),
        price=Decimal("2.85"),
        quantity=-1,
        strike=45,
        type=OptionType.PUT,
    )
    margin = calculate_margin([put], underlying)
    assert margin.cash_requirement == Decimal(4215)
    assert margin.margin_requirement == Decimal(935)


def test_short_leveraged_etf_broad():
    underlying = Underlying(
        price=460, etf_type=ETFType.BROAD, leverage_factor=Decimal("1.5")
    )
    put = Option(
        expiration=date.today(),
        price=4,
        quantity=-1,
        strike=390,
        type=OptionType.PUT,
    )
    margin = calculate_margin([put], underlying)
    assert margin.cash_requirement == Decimal(38600)
    assert margin.margin_requirement == Decimal(6250)


def test_short_call_itm():
    underlying = Underlying(price=Decimal("128.5"))
    call = Option(
        expiration=date.today(),
        price=Decimal("8.4"),
        quantity=-1,
        strike=120,
        type=OptionType.CALL,
    )
    margin = calculate_margin([call], underlying)
    assert margin.cash_requirement == Decimal(12010)
    assert margin.margin_requirement == Decimal(3410)


def test_short_call():
    underlying = Underlying(price=Decimal("26.38"))
    call = Option(
        expiration=date.today(),
        price=Decimal("0.05"),
        quantity=-1,
        strike=30,
        type=OptionType.CALL,
    )
    margin = calculate_margin([call], underlying)
    assert margin.cash_requirement == Decimal(2633)
    assert margin.margin_requirement == Decimal(269)


def test_short_call_leveraged_itm():
    underlying = Underlying(
        price=Decimal("815.5"), leverage_factor=2, etf_type=ETFType.NARROW
    )
    call = Option(
        expiration=date.today(),
        price=Decimal("10.1"),
        quantity=-1,
        strike=810,
        type=OptionType.CALL,
    )
    margin = calculate_margin([call], underlying)
    assert margin.cash_requirement == Decimal(80540)
    assert margin.margin_requirement == Decimal(33630)


def test_short_call_leveraged():
    underlying = Underlying(price=Decimal("1050.3"), leverage_factor=Decimal("1.5"))
    call = Option(
        expiration=date.today(),
        price=2,
        quantity=-1,
        strike=1250,
        type=OptionType.CALL,
    )
    margin = calculate_margin([call], underlying)
    assert margin.cash_requirement == Decimal(104830)
    assert margin.margin_requirement == Decimal(15954)


def test_short_call_broad_itm():
    underlying = Underlying(price=Decimal("433.35"), etf_type=ETFType.BROAD)
    call = Option(
        expiration=date.today(),
        price=Decimal("8.7"),
        quantity=-1,
        strike=430,
        type=OptionType.CALL,
    )
    margin = calculate_margin([call], underlying)
    assert margin.cash_requirement == Decimal(42130)
    assert margin.margin_requirement == Decimal(7370)


def test_short_call_broad():
    underlying = Underlying(price=Decimal("43.34"), etf_type=ETFType.BROAD)
    call = Option(
        expiration=date.today(),
        price=Decimal("1.35"),
        quantity=-1,
        strike=45,
        type=OptionType.CALL,
    )
    margin = calculate_margin([call], underlying)
    assert margin.cash_requirement == Decimal(4365)
    assert margin.margin_requirement == Decimal(619)


def test_short_call_etf_broad():
    underlying = Underlying(price=Decimal("378.5"), etf_type=ETFType.BROAD)
    call = Option(
        expiration=date.today(),
        price=Decimal("12.85"),
        quantity=-1,
        strike=370,
        type=OptionType.CALL,
    )
    margin = calculate_margin([call], underlying)
    assert margin.cash_requirement == Decimal(35715)
    assert margin.margin_requirement == Decimal(6962)


def test_short_call_broad_leveraged():
    underlying = Underlying(
        price=410, etf_type=ETFType.BROAD, leverage_factor=Decimal("1.5")
    )
    call = Option(
        expiration=date.today(),
        price=3,
        quantity=-1,
        strike=450,
        type=OptionType.CALL,
    )
    margin = calculate_margin([call], underlying)
    assert margin.cash_requirement == Decimal(44700)
    assert margin.margin_requirement == Decimal(6450)


def test_put_debit_spread():
    underlying = Underlying(price=255)
    long = Option(
        expiration=date.today(),
        price=3,
        quantity=1,
        strike=250,
        type=OptionType.PUT,
    )
    short = Option(
        expiration=date.today(),
        price=Decimal("0.95"),
        quantity=-1,
        strike=240,
        type=OptionType.PUT,
    )
    margin = calculate_margin([long, short], underlying)
    assert margin.cash_requirement == Decimal(205)
    assert margin.margin_requirement == Decimal(205)


def test_put_credit_spread():
    underlying = Underlying(price=Decimal("433.35"), etf_type=ETFType.BROAD)
    long = Option(
        expiration=date.today(),
        price=Decimal("6.4"),
        quantity=1,
        strike=425,
        type=OptionType.PUT,
    )
    short = Option(
        expiration=date.today(),
        price=Decimal("7.8"),
        quantity=-1,
        strike=430,
        type=OptionType.PUT,
    )
    margin = calculate_margin([long, short], underlying)
    assert margin.cash_requirement == Decimal(360)
    assert margin.margin_requirement == Decimal(360)


def test_put_credit_spread_itm():
    underlying = Underlying(price=Decimal("43.34"), etf_type=ETFType.NARROW)
    long = Option(
        expiration=date.today(),
        price=2,
        quantity=1,
        strike=Decimal("42.5"),
        type=OptionType.PUT,
    )
    short = Option(
        expiration=date.today(),
        price=Decimal("2.9"),
        quantity=-1,
        strike=45,
        type=OptionType.PUT,
    )
    margin = calculate_margin([long, short], underlying)
    assert margin.cash_requirement == Decimal(160)
    assert margin.margin_requirement == Decimal(160)


def test_call_credit_spread_itm():
    underlying = Underlying(price=Decimal("128.5"))
    long = Option(
        expiration=date.today(),
        price=Decimal("3.8"),
        quantity=1,
        strike=125,
        type=OptionType.CALL,
    )
    short = Option(
        expiration=date.today(),
        price=Decimal("8.4"),
        quantity=-1,
        strike=120,
        type=OptionType.CALL,
    )
    margin = calculate_margin([long, short], underlying)
    assert margin.cash_requirement == Decimal(40)
    assert margin.margin_requirement == Decimal(40)


def test_call_credit_calendar_spread():
    underlying = Underlying(price=75)
    long = Option(
        expiration=date.today(),
        price=5,
        quantity=1,
        strike=70,
        type=OptionType.CALL,
    )
    short = Option(
        expiration=date.today() + timedelta(days=30),
        price=8,
        quantity=-1,
        strike=70,
        type=OptionType.CALL,
    )
    margin = calculate_margin([long, short], underlying)
    assert margin.cash_requirement == Decimal(7200)
    assert margin.margin_requirement == Decimal(2800)

    assert margin == calculate_margin([long], underlying) + calculate_margin(
        [short], underlying
    )


def test_call_debit_calendar_spread():
    underlying = Underlying(price=75)
    long = Option(
        expiration=date.today() + timedelta(days=1),
        price=6,
        quantity=1,
        strike=70,
        type=OptionType.CALL,
    )
    short = Option(
        expiration=date.today(),
        price=5,
        quantity=-1,
        strike=70,
        type=OptionType.CALL,
    )
    margin = calculate_margin([long, short], underlying)
    assert margin.cash_requirement == Decimal(100)
    assert margin.margin_requirement == Decimal(100)


def test_call_calendar_spread_broad():
    underlying = Underlying(price=Decimal("433.35"), etf_type=ETFType.BROAD)
    long = Option(
        expiration=date.today(),
        price=Decimal("13.1"),
        quantity=1,
        strike=425,
        type=OptionType.CALL,
    )
    short = Option(
        expiration=date.today() + timedelta(days=30),
        price=Decimal("12.2"),
        quantity=-1,
        strike=430,
        type=OptionType.CALL,
    )
    margin = calculate_margin([long, short], underlying)
    assert margin.cash_requirement == Decimal(43090)
    assert margin.margin_requirement == Decimal(9030)


def test_straddle():
    underlying = Underlying(price=Decimal("92.63"))
    call = Option(
        expiration=date.today(),
        price=7,
        quantity=-1,
        strike=90,
        type=OptionType.CALL,
    )
    put = Option(
        expiration=date.today(),
        price=Decimal("3.7"),
        quantity=-1,
        strike=90,
        type=OptionType.PUT,
    )
    margin = calculate_margin([put, call], underlying)
    assert margin.cash_requirement == Decimal(17193)
    assert margin.margin_requirement == Decimal(2923)


def test_straddle_broad():
    underlying = Underlying(price=Decimal("433.35"), etf_type=ETFType.BROAD)
    call = Option(
        expiration=date.today(),
        price=Decimal("5.5"),
        quantity=-1,
        strike=435,
        type=OptionType.CALL,
    )
    put = Option(
        expiration=date.today(),
        price=Decimal("7.2"),
        quantity=-1,
        strike=435,
        type=OptionType.PUT,
    )
    margin = calculate_margin([put, call], underlying)
    assert margin.cash_requirement == Decimal(85730)
    assert margin.margin_requirement == Decimal(7770)


def test_straddle_broad_2():
    underlying = Underlying(price=Decimal("43.34"), etf_type=ETFType.BROAD)
    call = Option(
        expiration=date.today(),
        price=Decimal("1.35"),
        quantity=-1,
        strike=45,
        type=OptionType.CALL,
    )
    put = Option(
        expiration=date.today(),
        price=Decimal("2.85"),
        quantity=-1,
        strike=45,
        type=OptionType.PUT,
    )
    margin = calculate_margin([put, call], underlying)
    assert margin.cash_requirement == Decimal(8580)
    assert margin.margin_requirement == Decimal(1070)


def test_long_put_butterfly():
    underlying = Underlying(price=550)
    below = Option(
        expiration=date.today(),
        price=Decimal("5.6"),
        quantity=1,
        strike=540,
        type=OptionType.PUT,
    )
    short = Option(
        expiration=date.today(),
        price=Decimal("7.2"),
        quantity=-2,
        strike=550,
        type=OptionType.PUT,
    )
    above = Option(
        expiration=date.today(),
        price=Decimal("9.8"),
        quantity=1,
        strike=555,
        type=OptionType.PUT,
    )
    margin = calculate_margin([below, short, above], underlying)
    assert margin.cash_requirement == Decimal(600)
    assert margin.margin_requirement == Decimal(600)


def test_long_call_butterfly():
    underlying = Underlying(price=550)
    below = Option(
        expiration=date.today(),
        price=Decimal("12.4"),
        quantity=1,
        strike=545,
        type=OptionType.CALL,
    )
    short = Option(
        expiration=date.today(),
        price=Decimal("8.8"),
        quantity=-2,
        strike=550,
        type=OptionType.CALL,
    )
    above = Option(
        expiration=date.today(),
        price=2,
        quantity=1,
        strike=565,
        type=OptionType.CALL,
    )
    margin = calculate_margin([below, short, above], underlying)
    assert margin.cash_requirement == Decimal(680)
    assert margin.margin_requirement == Decimal(680)


def test_long_put_condor():
    underlying = Underlying(price=1160)
    long_below = Option(
        expiration=date.today(),
        price=Decimal("47.1"),
        quantity=1,
        strike=1050,
        type=OptionType.PUT,
    )
    short_below = Option(
        expiration=date.today(),
        price=Decimal("55.7"),
        quantity=-1,
        strike=1075,
        type=OptionType.PUT,
    )
    short_above = Option(
        expiration=date.today(),
        price=Decimal("66.3"),
        quantity=-1,
        strike=1100,
        type=OptionType.PUT,
    )
    long_above = Option(
        expiration=date.today(),
        price=Decimal("85.4"),
        quantity=1,
        strike=1125,
        type=OptionType.PUT,
    )
    margin = calculate_margin(
        [long_below, short_below, long_above, short_above], underlying
    )
    assert margin.cash_requirement == Decimal(1050)
    assert margin.margin_requirement == Decimal(1050)


def test_long_call_condor():
    underlying = Underlying(price=Decimal("26.75"))
    long_below = Option(
        expiration=date.today(),
        price=Decimal("0.45"),
        quantity=1,
        strike=Decimal("22.5"),
        type=OptionType.CALL,
    )
    short_below = Option(
        expiration=date.today(),
        price=Decimal("0.75"),
        quantity=-1,
        strike=25,
        type=OptionType.CALL,
    )
    short_above = Option(
        expiration=date.today(),
        price=Decimal("2.75"),
        quantity=-1,
        strike=30,
        type=OptionType.CALL,
    )
    long_above = Option(
        expiration=date.today(),
        price=Decimal("4.3"),
        quantity=1,
        strike=Decimal("32.5"),
        type=OptionType.CALL,
    )
    margin = calculate_margin(
        [long_below, short_below, long_above, short_above], underlying
    )
    assert margin.cash_requirement == Decimal(125)
    assert margin.margin_requirement == Decimal(125)


def test_iron_butterfly():
    underlying = Underlying(price=Decimal("26.75"))
    long_below = Option(
        expiration=date.today(),
        price=Decimal("0.1"),
        quantity=1,
        strike=16,
        type=OptionType.PUT,
    )
    short_below = Option(
        expiration=date.today(),
        price=Decimal("0.2"),
        quantity=-1,
        strike=20,
        type=OptionType.PUT,
    )
    short_above = Option(
        expiration=date.today(),
        price=7,
        quantity=-1,
        strike=20,
        type=OptionType.CALL,
    )
    long_above = Option(
        expiration=date.today(),
        price=4,
        quantity=1,
        strike=24,
        type=OptionType.CALL,
    )
    margin = calculate_margin(
        [long_below, short_below, long_above, short_above], underlying
    )
    assert margin.cash_requirement == Decimal(90)
    assert margin.margin_requirement == Decimal(90)


def test_iron_condor():
    underlying = Underlying(price=1060)
    long_below = Option(
        expiration=date.today(),
        price=32,
        quantity=1,
        strike=1000,
        type=OptionType.PUT,
    )
    short_below = Option(
        expiration=date.today(),
        price=Decimal("35.1"),
        quantity=-1,
        strike=1025,
        type=OptionType.PUT,
    )
    short_above = Option(
        expiration=date.today(),
        price=Decimal("9.4"),
        quantity=-1,
        strike=1150,
        type=OptionType.CALL,
    )
    long_above = Option(
        expiration=date.today(),
        price=Decimal("6.3"),
        quantity=1,
        strike=1175,
        type=OptionType.CALL,
    )
    margin = calculate_margin(
        [long_below, short_below, long_above, short_above], underlying
    )
    assert margin.cash_requirement == Decimal(1880)
    assert margin.margin_requirement == Decimal(1880)


def test_iron_condor_and_calendar_and_strangle():
    underlying = Underlying(price=1060)
    today = date.today()
    tomorrow = today + timedelta(days=1)
    long_below = Option(
        expiration=today,
        price=32,
        quantity=1,
        strike=1000,
        type=OptionType.PUT,
    )
    short_below = Option(
        expiration=today,
        price=Decimal("35.1"),
        quantity=-1,
        strike=1025,
        type=OptionType.PUT,
    )
    short_above = Option(
        expiration=today,
        price=Decimal("9.4"),
        quantity=-1,
        strike=1150,
        type=OptionType.CALL,
    )
    long_above = Option(
        expiration=today,
        price=Decimal("6.3"),
        quantity=1,
        strike=1175,
        type=OptionType.CALL,
    )
    strangle_put = Option(
        expiration=tomorrow,
        price=Decimal("37.5"),
        quantity=-1,
        strike=1025,
        type=OptionType.PUT,
    )
    strangle_call = Option(
        expiration=tomorrow,
        price=Decimal("6.5"),
        quantity=-1,
        strike=1175,
        type=OptionType.CALL,
    )
    calendar_short = Option(
        expiration=tomorrow,
        price=Decimal("25.3"),
        quantity=-1,
        strike=1150,
        type=OptionType.PUT,
    )
    calendar_long = Option(
        expiration=today,
        price=Decimal("28.3"),
        quantity=1,
        strike=1150,
        type=OptionType.PUT,
    )
    all = [
        long_below,
        short_below,
        long_above,
        short_above,
        strangle_call,
        strangle_put,
        calendar_long,
        calendar_short,
    ]
    random.shuffle(all)
    aggregate = calculate_margin(all, underlying)
    condor = calculate_margin(
        [long_below, short_below, long_above, short_above], underlying
    )
    strangle = calculate_margin([strangle_call, strangle_put], underlying)
    calendar = calculate_margin([calendar_long, calendar_short], underlying)
    assert aggregate == condor + strangle + calendar


def test_ratio_spread_call():
    underlying = Underlying(price=100)
    long = Option(
        expiration=date.today(),
        price=5,
        quantity=1,
        strike=110,
        type=OptionType.CALL,
    )
    short = Option(
        expiration=date.today(),
        price=10,
        quantity=-2,
        strike=105,
        type=OptionType.CALL,
    )
    margin = calculate_margin([long, short], underlying)
    single = short.model_copy(update={"quantity": -1})
    spread_margin = calculate_margin([long, single], underlying)
    naked_margin = calculate_margin([single], underlying)
    assert margin == spread_margin + naked_margin


def test_diagonal_spread():
    underlying = Underlying(price=50)
    today = date.today()
    tomorrow = today + timedelta(days=1)
    long = Option(
        expiration=tomorrow,
        price=2,
        quantity=1,
        strike=55,
        type=OptionType.CALL,
    )
    short = Option(
        expiration=today,
        price=4,
        quantity=-1,
        strike=52,
        type=OptionType.CALL,
    )
    margin = calculate_margin([long, short], underlying)
    # $200 credit from $3 width = $1
    assert margin.cash_requirement == Decimal(100)
    assert margin.margin_requirement == Decimal(100)


def test_multiple_strangles_with_remainders():
    underlying = Underlying(price=100)
    calls = Option(
        expiration=date.today(),
        price=3,
        quantity=-5,
        strike=110,
        type=OptionType.CALL,
    )
    puts = Option(
        expiration=date.today(),
        price=4,
        quantity=-3,
        strike=90,
        type=OptionType.PUT,
    )
    margin = calculate_margin([calls, puts], underlying)
    strangles = calculate_margin(
        [
            calls.model_copy(update={"quantity": -3}),
            puts,
        ],
        underlying,
    )
    naked_calls = calculate_margin(
        [calls.model_copy(update={"quantity": -2})], underlying
    )
    assert margin == strangles + naked_calls


def test_complex_multi_strategy_position():
    underlying = Underlying(price=500)
    today = date.today()
    tomorrow = today + timedelta(days=1)
    # vertical call spread $3 credit x2
    vertical_long = Option(
        expiration=today, price=10, quantity=2, strike=510, type=OptionType.CALL
    )
    vertical_short = Option(
        expiration=today, price=13, quantity=-2, strike=505, type=OptionType.CALL
    )
    # calendar put spread $5 debit
    calendar_long = Option(
        expiration=tomorrow, price=20, quantity=1, strike=495, type=OptionType.PUT
    )
    calendar_short = Option(
        expiration=today, price=15, quantity=-1, strike=495, type=OptionType.PUT
    )
    # naked strangle $11 credit x3 + naked call $5 credit
    strangle_call = Option(
        expiration=today, price=5, quantity=-3, strike=520, type=OptionType.CALL
    )
    strangle_put = Option(
        expiration=today, price=6, quantity=-2, strike=480, type=OptionType.PUT
    )
    # extra long that will match extra short from strangle
    orphan_long = Option(
        expiration=today, price=2, quantity=1, strike=530, type=OptionType.CALL
    )
    all = [
        vertical_long,
        vertical_short,
        calendar_long,
        calendar_short,
        strangle_call,
        strangle_put,
        orphan_long,
    ]
    random.shuffle(all)
    total = calculate_margin(all, underlying)
    mismatched_spread = calculate_margin(
        [strangle_put.model_copy(update={"quantity": -1}), calendar_long], underlying
    )
    vertical = calculate_margin([vertical_long, vertical_short], underlying)
    orphan_spread = calculate_margin(
        [strangle_call.model_copy(update={"quantity": -1}), orphan_long], underlying
    )
    strangle = calculate_margin(
        [
            strangle_call.model_copy(update={"quantity": -2}),
            strangle_put.model_copy(update={"quantity": -1}),
            calendar_short,
        ],
        underlying,
    )
    assert total == vertical + orphan_spread + strangle + mismatched_spread
