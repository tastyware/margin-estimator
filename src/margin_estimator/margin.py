from collections import deque
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
    # sort by expiry to cover near-term risk first
    shorts = sorted(leg for leg in legs if leg.quantity < 0)
    longs = {
        leg: leg.quantity for leg in sorted([leg for leg in legs if leg.quantity > 0])
    }
    covered: list[Option] = []
    naked_shorts: list[Option] = []

    # step 1: match spreads
    for short in shorts:
        unmatched = abs(short.quantity)
        # iterate our long inventory to find a cover
        for long, available in longs.items():
            if unmatched <= 0:
                break
            if available <= 0:
                continue
            # constraint: same type, long expiry >= short expiry
            if long.type == short.type and long.expiration >= short.expiration:
                paired = min(unmatched, available)
                covered.append(short.model_copy(update={"quantity": -paired}))
                covered.append(long.model_copy(update={"quantity": paired}))
                unmatched -= paired
                longs[long] -= paired

        # remaining short quantity is naked
        if unmatched > 0:
            naked_shorts.append(short.model_copy(update={"quantity": -unmatched}))

    # step 2: match strangles
    strangles: list[tuple[Option, Option]] = []
    naked_calls = deque(leg for leg in naked_shorts if leg.type == OptionType.CALL)
    naked_puts = deque(leg for leg in naked_shorts if leg.type == OptionType.PUT)

    while naked_calls and naked_puts:
        call = naked_calls.popleft()
        put = naked_puts.popleft()
        q = min(abs(call.quantity), abs(put.quantity))
        strangles.append(
            (
                call.model_copy(update={"quantity": -q}),
                put.model_copy(update={"quantity": -q}),
            )
        )
        # handle remaining quantity
        if rem := abs(call.quantity) - q:
            naked_calls.appendleft(call.model_copy(update={"quantity": -rem}))
        if rem := abs(put.quantity) - q:
            naked_puts.appendleft(put.model_copy(update={"quantity": -rem}))

    # all unmatched options at this point go here
    naked = list(naked_calls)
    naked.extend(naked_puts)
    naked.extend(
        leg.model_copy(update={"quantity": q}) for leg, q in longs.items() if q
    )

    # step 3: calculate totals
    total = MarginRequirements(cash_requirement=ZERO, margin_requirement=ZERO)
    if covered:
        total += _calculate_margin_spread(covered)
    for call, put in strangles:
        total += _calculate_margin_short_strangle([call, put], underlying)
    for leg in naked:
        if leg.quantity > 0:
            total += _calculate_margin_long_option(leg)
        else:
            total += _calculate_margin_short_option(leg, underlying)

    return total


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
