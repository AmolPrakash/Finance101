"""Chapter 17 - The term structure of interest rates.

Different maturities earn different yields. Spot rates price zero-coupon
cash flows; forward rates are the rates implied for future periods.
All rates here are annual and compounded annually.
"""

from typing import List, Sequence


def discount_factor(spot_rate: float, years: float) -> float:
    return 1 / (1 + spot_rate) ** years


def forward_rate(spot_short: float, t_short: float, spot_long: float, t_long: float) -> float:
    """Rate locked in today for borrowing between t_short and t_long.

    (1 + s_long)^t_long = (1 + s_short)^t_short x (1 + f)^(t_long - t_short)
    """
    growth = (1 + spot_long) ** t_long / (1 + spot_short) ** t_short
    return growth ** (1 / (t_long - t_short)) - 1


def bootstrap_spot_rates(par_yields: Sequence[float]) -> List[float]:
    """Spot rates for years 1..n from par yields of annual-coupon bonds.

    A par bond with coupon c maturing at n satisfies:
        1 = c x sum(DF_1..DF_n) + DF_n
    """
    discount_factors: List[float] = []
    spots: List[float] = []
    for n, coupon in enumerate(par_yields, start=1):
        df_n = (1 - coupon * sum(discount_factors)) / (1 + coupon)
        discount_factors.append(df_n)
        spots.append(df_n ** (-1 / n) - 1)
    return spots


def price_from_spot_curve(cash_flows: Sequence[float], spot_rates: Sequence[float]) -> float:
    """Price annual cash flows (years 1..n) with each year's own spot rate."""
    return sum(cf * discount_factor(s, t) for t, (cf, s) in enumerate(zip(cash_flows, spot_rates), start=1))
