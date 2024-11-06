from datetime import date, timedelta
from decimal import Decimal

from .models import (
    ETFType,
    MarginRequirements,
    Option,
    OptionType,
    Underlying,
)

ZERO = Decimal(0)


def calculate_margin(legs: list[Option], underlying: Underlying) -> MarginRequirements:
    """
    Calculate margin for an arbitrary order according to CBOE's Margin Manual.
    """
    if len(legs) == 1:
        if legs[0].quantity > 0:
            return _calculate_margin_long_option(legs[0])
        return _calculate_margin_short_option(legs[0], underlying)
    if len(legs) == 2 and legs[0].quantity < 0 and legs[1].quantity < 0:
        return _calculate_margin_short_strangle(legs, underlying)
    if len(legs) == 2 and legs[0].expiration != legs[1].expiration:
        short = legs[0] if legs[0].quantity < 0 else legs[1]
        long = legs[1] if legs[1] != short else legs[0]
        if short.expiration > long.expiration:
            margin = _calculate_margin_short_option(short, underlying)
            return margin + _calculate_margin_long_option(long)
    calls = [leg for leg in legs if leg.type == OptionType.CALL]
    puts = [leg for leg in legs if leg.type == OptionType.PUT]
    extra_puts = sum(c.quantity for c in calls)
    extra_calls = sum(p.quantity for p in puts)
    if extra_puts or extra_calls:
        raise Exception(
            "Ratio spreads/complex orders not supported! Try splitting your order into "
            "smaller components and summing the results."
        )
    return _calculate_margin_spread(legs)


def _calculate_margin_long_option(option: Option) -> MarginRequirements:
    """
    Calculate margin for a single long option.
    Source: CBOE Margin Manual
    """
    if option.expiration < date.today() + timedelta(days=90):
        return MarginRequirements(
            # Pay for each put or call in full.
            cash_requirement=option.price * 100 * option.quantity,
            # Pay for each put or call in full.
            margin_requirement=option.price * 100 * option.quantity,
        )
    reduced_requirement = round(option.price * 3 / 4, 2)
    return MarginRequirements(
        # Pay for each put or call in full.
        cash_requirement=option.price * 100 * option.quantity,
        # Listed: 75% of the total cost of the option.
        margin_requirement=reduced_requirement * 100 * option.quantity,
    )


def _calculate_margin_short_option(
    option: Option, underlying: Underlying
) -> MarginRequirements:
    """
    Calculate margin for a single short option.
    Source: CBOE Margin Manual
    """
    if option.type == OptionType.PUT:
        otm_distance = max(ZERO, underlying.price - option.strike)
    else:
        otm_distance = max(ZERO, option.strike - underlying.price)
    # broad-based ETFs/indices
    if underlying.etf_type == ETFType.BROAD:
        if option.type == OptionType.PUT:
            minimum = round(
                option.price + option.strike / 10 * underlying.leverage_factor, 2
            )
            base = round(
                option.price
                + underlying.price * 3 / 20 * underlying.leverage_factor
                - otm_distance,
                2,
            )
            # 100% of option proceeds plus 15% of underlying index value less
            # out-of-the money amount, if any, to a minimum for puts of option
            # proceeds plus 10% of the put’s exercise price.
            margin_requirement = max(minimum, base)
            # Deposit cash or cash equivalents equal to aggregate exercise price
            cash_requirement = (option.strike - option.price) * 100
        else:  # OptionType.CALL
            minimum = round(
                option.price + underlying.price / 10 * underlying.leverage_factor, 2
            )
            base = round(
                option.price
                + underlying.price * 3 / 20 * underlying.leverage_factor
                - otm_distance,
                2,
            )
            # 100% of option proceeds plus 15% of underlying index value less
            # out-of-the money amount, if any, to a minimum for calls of option
            # proceeds plus 10% of the underlying index value.
            margin_requirement = max(minimum, base)
            # Deposit cash or cash equivalents equal to aggregate exercise price
            cash_requirement = (option.strike - option.price) * 100
    # narrow-based ETFs/indices, volatility indices, equities
    else:
        if option.type == OptionType.PUT:
            minimum = round(
                option.price + option.strike / 10 * underlying.leverage_factor, 2
            )
            base = round(
                option.price
                + underlying.price / 5 * underlying.leverage_factor
                - otm_distance,
                2,
            )
            # 100% of option proceeds plus 20% of underlying security / index value
            # less out-of-the-money amount, if any, to a minimum for puts of option
            # proceeds plus 10% of the put’s exercise price.
            margin_requirement = max(minimum, base)
            # Deposit cash or cash equivalents equal to aggregate exercise price.
            cash_requirement = (option.strike - option.price) * 100
        else:  # OptionType.CALL
            minimum = round(
                option.price + underlying.price / 10 * underlying.leverage_factor, 2
            )
            base = round(
                option.price
                + underlying.price / 5 * underlying.leverage_factor
                - otm_distance,
                2,
            )
            # 100% of option proceeds plus 20% of underlying security / index value
            # less out-of-the-money amount, if any, to a minimum for puts of option
            # proceeds plus 10% of the underlying security/index value.
            margin_requirement = max(minimum, base)
            # Deposit underlying security.
            cash_requirement = (underlying.price - option.price) * 100
    margin_requirement *= 100 * abs(option.quantity)
    return MarginRequirements(
        cash_requirement=cash_requirement,
        margin_requirement=margin_requirement,
    )


def _calculate_margin_short_strangle(
    legs: list[Option], underlying: Underlying
) -> MarginRequirements:
    """
    Calculate margin for a short strangle.
    Source: CBOE Margin Manual
    """
    # Deposit an escrow agreement for each option.
    margin1 = _calculate_margin_short_option(legs[0], underlying)
    margin2 = _calculate_margin_short_option(legs[1], underlying)
    # For the same underlying security, short put or short call requirement whichever
    # is greater, plus the option proceeds of the other side.
    if margin1.margin_requirement > margin2.margin_requirement:
        margin_requirement = margin1.margin_requirement + legs[1].price * 100
    else:
        margin_requirement = margin2.margin_requirement + legs[0].price * 100
    margin_requirement *= abs(legs[0].quantity)
    return MarginRequirements(
        cash_requirement=margin1.cash_requirement + margin2.cash_requirement,
        margin_requirement=margin_requirement,
    )


def _calculate_loss_for(leg: Option, price: Decimal) -> Decimal:
    """
    Calculate value at expiration for option at given price.
    """
    if leg.type == OptionType.CALL:
        itm_distance = max(ZERO, price - leg.strike)
    else:
        itm_distance = max(ZERO, leg.strike - price)
    return itm_distance * leg.quantity * 100


def _get_net_credit_or_debit(legs: list[Option]) -> Decimal:
    """
    Calculate total debit/credit paid/collected for the order.
    """
    total = ZERO
    for leg in legs:
        total += leg.quantity * leg.price * 100
    return total


def _calculate_margin_spread(legs: list[Option]) -> MarginRequirements:
    """
    Calculate margin for a credit spread.
    Source: CBOE Margin Manual
    """
    strikes = set(leg.strike for leg in legs)
    pnl = _get_net_credit_or_debit(legs)
    losses = []
    for strike in strikes:
        points = [_calculate_loss_for(leg, strike) for leg in legs]
        losses.append(sum(points))  # type: ignore
    margin_requirement = abs(min(losses)) + pnl

    return MarginRequirements(
        # deposit and maintain cash or cash equivalents equal to the spread’s maximum
        # potential loss
        cash_requirement=margin_requirement,
        # the lesser of the amount required for the short option(s), or the spread’s
        # maximum potential loss
        margin_requirement=margin_requirement,
    )
