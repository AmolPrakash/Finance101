"""Chapter 11 - Stock valuation.

A stock is worth the present value of the cash it will pay its owners.
Dividend discount models (DDM) make that idea concrete.
"""

from typing import Sequence


def gordon_growth_value(next_dividend: float, required_return: float, growth: float) -> float:
    """Constant-growth DDM: P0 = D1 / (r - g), valid only when r > g."""
    if required_return <= growth:
        raise ValueError("required_return must exceed growth")
    return next_dividend / (required_return - growth)


def implied_required_return(price: float, next_dividend: float, growth: float) -> float:
    """Rearranged Gordon model: r = D1 / P0 + g (dividend yield + growth)."""
    return next_dividend / price + growth


def two_stage_ddm(current_dividend: float, required_return: float, high_growth: float,
                  high_growth_years: int, terminal_growth: float) -> float:
    """Dividends grow fast for a few years, then settle to a stable rate forever."""
    value = 0.0
    dividend = current_dividend
    for year in range(1, high_growth_years + 1):
        dividend *= 1 + high_growth
        value += dividend / (1 + required_return) ** year
    terminal_value = gordon_growth_value(dividend * (1 + terminal_growth), required_return, terminal_growth)
    return value + terminal_value / (1 + required_return) ** high_growth_years


def dcf_value(free_cash_flows: Sequence[float], discount_rate: float, terminal_growth: float) -> float:
    """Enterprise value from explicit free cash flows (years 1..n) plus a terminal value."""
    value = sum(fcf / (1 + discount_rate) ** t for t, fcf in enumerate(free_cash_flows, start=1))
    n = len(free_cash_flows)
    terminal = gordon_growth_value(free_cash_flows[-1] * (1 + terminal_growth), discount_rate, terminal_growth)
    return value + terminal / (1 + discount_rate) ** n


def price_to_earnings(price: float, earnings_per_share: float) -> float:
    """P/E multiple: how many dollars investors pay per dollar of earnings."""
    return price / earnings_per_share
