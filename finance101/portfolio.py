"""Lesson 07 - Portfolios, diversification and CAPM.

Combining assets that don't move in lockstep lowers risk without necessarily
lowering return -- the only "free lunch" in finance.
"""

import statistics
from typing import List, Sequence


def portfolio_return(weights: Sequence[float], expected_returns: Sequence[float]) -> float:
    """Weighted average of the assets' expected returns."""
    return sum(w * r for w, r in zip(weights, expected_returns))


def covariance_matrix(return_series: Sequence[Sequence[float]]) -> List[List[float]]:
    """Sample covariance matrix from one return series per asset."""
    return [[statistics.covariance(a, b) for b in return_series] for a in return_series]


def portfolio_variance(weights: Sequence[float], cov_matrix: Sequence[Sequence[float]]) -> float:
    """w^T * Sigma * w"""
    n = len(weights)
    return sum(weights[i] * weights[j] * cov_matrix[i][j] for i in range(n) for j in range(n))


def portfolio_volatility(weights: Sequence[float], cov_matrix: Sequence[Sequence[float]]) -> float:
    return portfolio_variance(weights, cov_matrix) ** 0.5


def two_asset_volatility(w1: float, vol1: float, vol2: float, correlation: float) -> float:
    """Volatility of a two-asset portfolio; shows how correlation drives diversification."""
    w2 = 1 - w1
    variance = (w1 * vol1) ** 2 + (w2 * vol2) ** 2 + 2 * w1 * w2 * vol1 * vol2 * correlation
    return variance ** 0.5


def min_variance_weight(vol1: float, vol2: float, correlation: float) -> float:
    """Weight in asset 1 that minimizes two-asset portfolio volatility."""
    cov = correlation * vol1 * vol2
    return (vol2 ** 2 - cov) / (vol1 ** 2 + vol2 ** 2 - 2 * cov)


def beta(asset_returns: Sequence[float], market_returns: Sequence[float]) -> float:
    """Sensitivity of an asset to the market: Cov(asset, market) / Var(market)."""
    return statistics.covariance(asset_returns, market_returns) / statistics.variance(market_returns)


def capm_expected_return(risk_free_rate: float, beta_value: float, market_return: float) -> float:
    """CAPM: E[R] = Rf + beta * (E[Rm] - Rf)"""
    return risk_free_rate + beta_value * (market_return - risk_free_rate)


def wacc(equity_value: float, debt_value: float, cost_of_equity: float,
         cost_of_debt: float, tax_rate: float) -> float:
    """Weighted average cost of capital; debt is cheaper because interest is tax deductible."""
    total = equity_value + debt_value
    return (equity_value / total) * cost_of_equity + (debt_value / total) * cost_of_debt * (1 - tax_rate)
