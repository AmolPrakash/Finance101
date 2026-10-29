"""Chapters 02-04 - Time value of money, interest rates and annuities.

A dollar today is worth more than a dollar tomorrow because today's dollar
can be invested to earn a return. Every other topic in finance builds on the
functions in this module.

Conventions used throughout the package:
    rate     -- interest rate per period, as a decimal (5% -> 0.05)
    periods  -- number of compounding periods
    Cash you receive is positive; cash you pay is negative only where noted.
"""

import math


def future_value(present_value: float, rate: float, periods: float) -> float:
    """FV = PV * (1 + r)^n"""
    return present_value * (1 + rate) ** periods


def present_value(future_value: float, rate: float, periods: float) -> float:
    """PV = FV / (1 + r)^n"""
    return future_value / (1 + rate) ** periods


def future_value_continuous(present_value: float, rate: float, years: float) -> float:
    """FV with continuous compounding: PV * e^(r * t)"""
    return present_value * math.exp(rate * years)


def effective_annual_rate(nominal_rate: float, compounds_per_year: int) -> float:
    """Convert a nominal annual rate (APR) to the effective annual rate (EAR).

    EAR = (1 + APR / m)^m - 1
    """
    return (1 + nominal_rate / compounds_per_year) ** compounds_per_year - 1


def rule_of_72(rate: float) -> float:
    """Approximate years to double money at an annual rate (decimal)."""
    return 72 / (rate * 100)


def years_to_double(rate: float) -> float:
    """Exact years to double money: ln(2) / ln(1 + r)."""
    return math.log(2) / math.log(1 + rate)


def present_value_annuity(payment: float, rate: float, periods: int, due: bool = False) -> float:
    """PV of a level stream of payments.

    PV = PMT * [1 - (1 + r)^-n] / r
    An annuity *due* pays at the start of each period, so it is worth (1 + r) more.
    """
    if rate == 0:
        pv = payment * periods
    else:
        pv = payment * (1 - (1 + rate) ** -periods) / rate
    return pv * (1 + rate) if due else pv


def future_value_annuity(payment: float, rate: float, periods: int, due: bool = False) -> float:
    """FV of a level stream of payments.

    FV = PMT * [(1 + r)^n - 1] / r
    """
    if rate == 0:
        fv = payment * periods
    else:
        fv = payment * ((1 + rate) ** periods - 1) / rate
    return fv * (1 + rate) if due else fv


def present_value_perpetuity(payment: float, rate: float, growth: float = 0.0) -> float:
    """PV of payments that last forever, optionally growing at ``growth``.

    PV = PMT / (r - g), valid only when r > g. ``payment`` is the first payment,
    received one period from now.
    """
    if rate <= growth:
        raise ValueError("rate must be greater than growth for a perpetuity")
    return payment / (rate - growth)


def real_rate(nominal_rate: float, inflation: float) -> float:
    """Fisher equation: (1 + nominal) = (1 + real) * (1 + inflation)."""
    return (1 + nominal_rate) / (1 + inflation) - 1


def solve_rate(present_value: float, future_value: float, periods: float) -> float:
    """Rate per period that grows ``present_value`` into ``future_value``: (FV/PV)^(1/n) - 1"""
    return (future_value / present_value) ** (1 / periods) - 1


def solve_periods(present_value: float, future_value: float, rate: float) -> float:
    """Periods needed to grow ``present_value`` into ``future_value``: ln(FV/PV) / ln(1 + r)"""
    return math.log(future_value / present_value) / math.log(1 + rate)


def annuity_payment_for_goal(goal: float, rate: float, periods: int) -> float:
    """Level saving per period needed to reach ``goal`` (end-of-period deposits)."""
    if rate == 0:
        return goal / periods
    return goal * rate / ((1 + rate) ** periods - 1)
