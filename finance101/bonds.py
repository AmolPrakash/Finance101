"""Lesson 04 - Bonds.

A bond's price is the present value of its coupons plus its face value.
Prices and yields move in opposite directions; duration measures how much.

All functions take *annual* coupon rates and yields and a ``frequency``
(payments per year, e.g. 2 for semi-annual).
"""

from typing import List, Tuple


def _cash_flows(face: float, coupon_rate: float, years: float, frequency: int) -> List[Tuple[float, float]]:
    """Return (time_in_years, cash_flow) pairs for a plain-vanilla bond."""
    n = round(years * frequency)
    coupon = face * coupon_rate / frequency
    flows = [((t / frequency), coupon) for t in range(1, n + 1)]
    last_time, last_cf = flows[-1]
    flows[-1] = (last_time, last_cf + face)
    return flows


def bond_price(face: float, coupon_rate: float, ytm: float, years: float, frequency: int = 2) -> float:
    """Price = sum of coupon / (1 + y/f)^t + face / (1 + y/f)^n"""
    y = ytm / frequency
    return sum(cf / (1 + y) ** (t * frequency) for t, cf in _cash_flows(face, coupon_rate, years, frequency))


def yield_to_maturity(price: float, face: float, coupon_rate: float, years: float,
                      frequency: int = 2, tol: float = 1e-10) -> float:
    """Solve for the yield that makes the bond's price equal ``price`` (bisection)."""
    low, high = -0.99, 10.0
    for _ in range(1000):
        mid = (low + high) / 2
        # Price falls as yield rises, so a too-high model price means yield is too low.
        if bond_price(face, coupon_rate, mid, years, frequency) > price:
            low = mid
        else:
            high = mid
        if high - low < tol:
            break
    return (low + high) / 2


def current_yield(price: float, face: float, coupon_rate: float) -> float:
    """Annual coupon divided by price."""
    return face * coupon_rate / price


def macaulay_duration(face: float, coupon_rate: float, ytm: float, years: float, frequency: int = 2) -> float:
    """Weighted-average time (in years) until cash flows are received."""
    y = ytm / frequency
    flows = _cash_flows(face, coupon_rate, years, frequency)
    pvs = [(t, cf / (1 + y) ** (t * frequency)) for t, cf in flows]
    price = sum(pv for _, pv in pvs)
    return sum(t * pv for t, pv in pvs) / price


def modified_duration(face: float, coupon_rate: float, ytm: float, years: float, frequency: int = 2) -> float:
    """Approximate % price change for a 1.00 (100%) change in yield.

    Delta P / P ~= -ModDur * Delta y
    """
    return macaulay_duration(face, coupon_rate, ytm, years, frequency) / (1 + ytm / frequency)


def convexity(face: float, coupon_rate: float, ytm: float, years: float, frequency: int = 2) -> float:
    """Second-order sensitivity of price to yield (in years squared)."""
    y = ytm / frequency
    flows = _cash_flows(face, coupon_rate, years, frequency)
    price = bond_price(face, coupon_rate, ytm, years, frequency)
    total = 0.0
    for t, cf in flows:
        k = t * frequency
        total += cf * k * (k + 1) / (1 + y) ** (k + 2)
    return total / (price * frequency ** 2)
