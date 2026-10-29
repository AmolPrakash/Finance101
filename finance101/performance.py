"""Chapter 18 - Performance evaluation.

Was a fund manager skilled or just taking more risk? These ratios adjust
returns for the risk taken. Inputs are per-period returns; risk_free is the
per-period risk-free rate.
"""

import math
import statistics
from typing import Sequence


def _excess(returns: Sequence[float], risk_free: float):
    return [r - risk_free for r in returns]


def sortino_ratio(returns: Sequence[float], risk_free: float = 0.0, periods_per_year: int = 1) -> float:
    """Like Sharpe, but only penalizes downside volatility."""
    excess = _excess(returns, risk_free)
    downside = math.sqrt(sum(min(r, 0.0) ** 2 for r in excess) / len(excess))
    return statistics.mean(excess) / downside * math.sqrt(periods_per_year)


def treynor_ratio(returns: Sequence[float], beta_value: float, risk_free: float = 0.0,
                  periods_per_year: int = 1) -> float:
    """Excess return per unit of market (systematic) risk, annualized."""
    return statistics.mean(_excess(returns, risk_free)) * periods_per_year / beta_value


def jensens_alpha(returns: Sequence[float], market_returns: Sequence[float], risk_free: float = 0.0,
                  periods_per_year: int = 1) -> float:
    """Annualized return above what CAPM predicts for the fund's beta."""
    fund = _excess(returns, risk_free)
    market = _excess(market_returns, risk_free)
    beta_value = statistics.covariance(fund, market) / statistics.variance(market)
    return (statistics.mean(fund) - beta_value * statistics.mean(market)) * periods_per_year


def tracking_error(returns: Sequence[float], benchmark_returns: Sequence[float], periods_per_year: int = 1) -> float:
    """Volatility of the difference between fund and benchmark returns."""
    active = [r - b for r, b in zip(returns, benchmark_returns)]
    return statistics.stdev(active) * math.sqrt(periods_per_year)


def information_ratio(returns: Sequence[float], benchmark_returns: Sequence[float], periods_per_year: int = 1) -> float:
    """Active return per unit of active risk."""
    active = [r - b for r, b in zip(returns, benchmark_returns)]
    return statistics.mean(active) / statistics.stdev(active) * math.sqrt(periods_per_year)
