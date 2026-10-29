"""Chapter 19 - Forwards, futures and swaps.

These contracts lock in a price or rate today for a transaction later. Their
prices come from no-arbitrage: if the forward price were anything else, you
could earn a riskless profit. Rates here are continuously compounded.
"""

import math
from typing import Sequence


def forward_price(spot: float, rate: float, years: float, income_yield: float = 0.0,
                  storage_cost: float = 0.0) -> float:
    """F = S x e^((r + storage - q) T)

    ``income_yield`` (q) is a dividend yield or foreign interest rate;
    ``storage_cost`` is a continuous cost of carry for commodities.
    """
    return spot * math.exp((rate + storage_cost - income_yield) * years)


def fx_forward(spot: float, domestic_rate: float, foreign_rate: float, years: float) -> float:
    """Covered interest-rate parity. ``spot`` is domestic currency per unit of foreign."""
    return forward_price(spot, domestic_rate, years, income_yield=foreign_rate)


def forward_contract_value(spot: float, delivery_price: float, rate: float, years: float,
                           income_yield: float = 0.0) -> float:
    """Value today of a long forward agreed at ``delivery_price``."""
    return spot * math.exp(-income_yield * years) - delivery_price * math.exp(-rate * years)


def futures_pnl(entry_price: float, exit_price: float, contracts: float, multiplier: float) -> float:
    """Profit on a futures position (positive contracts = long)."""
    return (exit_price - entry_price) * contracts * multiplier


def hedge_ratio(spot_vol: float, futures_vol: float, correlation: float) -> float:
    """Minimum-variance hedge ratio h* = rho x sigma_S / sigma_F."""
    return correlation * spot_vol / futures_vol


def par_swap_rate(discount_factors: Sequence[float], payments_per_year: int = 1) -> float:
    """Fixed rate that makes a new interest-rate swap worth zero.

    swap rate = (1 - DF_n) / (sum of DF_i / payments_per_year)
    """
    annuity = sum(discount_factors) / payments_per_year
    return (1 - discount_factors[-1]) / annuity


def swap_value_receive_fixed(notional: float, fixed_rate: float, discount_factors: Sequence[float],
                             payments_per_year: int = 1) -> float:
    """Value to the party receiving fixed: fixed leg minus floating leg (worth par)."""
    fixed_leg = notional * fixed_rate / payments_per_year * sum(discount_factors) + notional * discount_factors[-1]
    return fixed_leg - notional
