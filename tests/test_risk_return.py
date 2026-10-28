import pytest

from finance101 import risk_return as rr


def test_returns():
    assert rr.simple_returns([100, 110, 99]) == pytest.approx([0.10, -0.10])
    assert rr.cumulative_return([0.10, -0.10]) == pytest.approx(-0.01)
    assert sum(rr.log_returns([100, 110, 99])) == pytest.approx(rr.log_returns([100, 99])[0])


def test_annualized_return():
    assert rr.annualized_return([0.10, 0.10], periods_per_year=1) == pytest.approx(0.10)
    assert rr.annualized_return([0.01] * 24, periods_per_year=12) == pytest.approx(1.01 ** 12 - 1)


def test_max_drawdown():
    assert rr.max_drawdown([100, 120, 90, 130]) == pytest.approx(-0.25)


def test_volatility_and_sharpe():
    returns = [0.01, -0.02, 0.03, 0.00, 0.02]
    assert rr.volatility(returns) > 0
    assert rr.sharpe_ratio(returns) > 0


def test_var():
    returns = [i / 100 for i in range(-10, 10)]  # 20 returns from -10% to +9%
    assert rr.historical_var(returns, 0.95) == pytest.approx(0.09)
