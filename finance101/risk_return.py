"""Chapter 14 - Risk and return.

Return measures what you earned; risk (volatility) measures how much that
return bounced around. Investors demand higher expected return for more risk.
"""

import math
import statistics
from typing import List, Sequence


def simple_returns(prices: Sequence[float]) -> List[float]:
    """Period-over-period returns: P_t / P_{t-1} - 1"""
    return [prices[i] / prices[i - 1] - 1 for i in range(1, len(prices))]


def log_returns(prices: Sequence[float]) -> List[float]:
    """Continuously compounded returns: ln(P_t / P_{t-1}). They add across time."""
    return [math.log(prices[i] / prices[i - 1]) for i in range(1, len(prices))]


def cumulative_return(returns: Sequence[float]) -> float:
    """Total growth from compounding a series of simple returns."""
    growth = 1.0
    for r in returns:
        growth *= 1 + r
    return growth - 1


def annualized_return(returns: Sequence[float], periods_per_year: int) -> float:
    """Geometric average return scaled to one year (CAGR)."""
    years = len(returns) / periods_per_year
    return (1 + cumulative_return(returns)) ** (1 / years) - 1


def volatility(returns: Sequence[float], periods_per_year: int = 1) -> float:
    """Sample standard deviation of returns, annualized by sqrt(periods_per_year)."""
    return statistics.stdev(returns) * math.sqrt(periods_per_year)


def sharpe_ratio(returns: Sequence[float], risk_free_rate: float = 0.0, periods_per_year: int = 1) -> float:
    """Excess return earned per unit of volatility (annualized).

    ``risk_free_rate`` is annual; it is converted to a per-period rate.
    """
    rf_per_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    excess = [r - rf_per_period for r in returns]
    return statistics.mean(excess) / statistics.stdev(excess) * math.sqrt(periods_per_year)


def max_drawdown(prices: Sequence[float]) -> float:
    """Largest peak-to-trough fall, returned as a negative decimal (e.g. -0.35)."""
    peak = prices[0]
    worst = 0.0
    for price in prices:
        peak = max(peak, price)
        worst = min(worst, price / peak - 1)
    return worst


def historical_var(returns: Sequence[float], confidence: float = 0.95) -> float:
    """Historical Value at Risk: the loss not exceeded with ``confidence`` probability.

    Returned as a positive number (0.03 means a 3% loss).
    """
    ordered = sorted(returns)
    index = int((1 - confidence) * len(ordered) + 1e-9)  # guard against 1.999... from float math
    return -ordered[index]


def expected_shortfall(returns: Sequence[float], confidence: float = 0.95) -> float:
    """Average loss in the worst (1 - confidence) tail (a.k.a. CVaR), as a positive number."""
    ordered = sorted(returns)
    cutoff = max(1, int((1 - confidence) * len(ordered) + 1e-9))
    return -statistics.mean(ordered[:cutoff])


def parametric_var(mean: float, stdev: float, confidence: float = 0.95) -> float:
    """Value at Risk assuming normally distributed returns, as a positive number."""
    z = statistics.NormalDist().inv_cdf(1 - confidence)
    return -(mean + z * stdev)
