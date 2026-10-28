"""Lesson 02 - Capital budgeting: deciding which projects are worth doing.

Cash flows are a list where index 0 is today (usually a negative investment)
and index t is the cash flow at the end of period t.
"""

from typing import Optional, Sequence


def npv(rate: float, cash_flows: Sequence[float]) -> float:
    """Net present value: sum of CF_t / (1 + r)^t, starting at t = 0.

    Rule: accept a project when NPV > 0 -- it creates value above the
    required return.
    """
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))


def irr(cash_flows: Sequence[float], low: float = -0.99, high: float = 10.0,
        tol: float = 1e-10, max_iter: int = 1000) -> float:
    """Internal rate of return: the rate where NPV = 0, found by bisection.

    Bisection is slower than Newton's method but always converges when the
    NPV changes sign between ``low`` and ``high``.
    """
    npv_low, npv_high = npv(low, cash_flows), npv(high, cash_flows)
    if npv_low * npv_high > 0:
        raise ValueError("NPV does not change sign in the search range; IRR not found")
    for _ in range(max_iter):
        mid = (low + high) / 2
        npv_mid = npv(mid, cash_flows)
        if abs(npv_mid) < tol:
            return mid
        if npv_low * npv_mid < 0:
            high = mid
        else:
            low, npv_low = mid, npv_mid
    return (low + high) / 2


def payback_period(cash_flows: Sequence[float]) -> Optional[float]:
    """Periods until cumulative cash flow turns non-negative (ignores time value).

    Returns None if the project never pays back.
    """
    cumulative = 0.0
    for t, cf in enumerate(cash_flows):
        previous = cumulative
        cumulative += cf
        if cumulative >= 0 and t > 0:
            # Interpolate within the period, assuming cash arrives evenly.
            return t - 1 + (-previous / cf)
    return None


def discounted_payback_period(rate: float, cash_flows: Sequence[float]) -> Optional[float]:
    """Payback period using discounted cash flows."""
    discounted = [cf / (1 + rate) ** t for t, cf in enumerate(cash_flows)]
    return payback_period(discounted)


def profitability_index(rate: float, cash_flows: Sequence[float]) -> float:
    """PV of future cash flows divided by the initial investment.

    PI > 1 is equivalent to NPV > 0.
    """
    initial = -cash_flows[0]
    if initial <= 0:
        raise ValueError("first cash flow must be a negative investment")
    return npv(rate, [0.0, *cash_flows[1:]]) / initial
