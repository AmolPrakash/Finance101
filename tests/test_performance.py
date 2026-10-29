import pytest

from finance101 import performance as perf

MARKET = [0.02, -0.01, 0.03, -0.02, 0.015, 0.01]


def test_alpha_of_levered_market_is_zero():
    fund = [1.5 * r for r in MARKET]
    assert perf.jensens_alpha(fund, MARKET) == pytest.approx(0, abs=1e-12)


def test_alpha_detects_constant_outperformance():
    fund = [r + 0.001 for r in MARKET]
    assert perf.jensens_alpha(fund, MARKET, periods_per_year=12) == pytest.approx(0.012)


def test_tracking_error_and_information_ratio():
    fund = [r + d for r, d in zip(MARKET, [0.001, -0.001] * 3)]
    assert perf.tracking_error(fund, MARKET) > 0
    assert perf.information_ratio(fund, MARKET) == pytest.approx(0, abs=1e-12)


def test_sortino_and_treynor():
    assert perf.sortino_ratio(MARKET) > 0
    assert perf.treynor_ratio([0.01, 0.02], beta_value=2) == pytest.approx(0.0075)
