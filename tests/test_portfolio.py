import pytest

from finance101 import portfolio as pf


def test_perfect_correlation_gives_no_diversification():
    assert pf.two_asset_volatility(0.5, 0.2, 0.1, 1.0) == pytest.approx(0.15)
    assert pf.two_asset_volatility(0.5, 0.2, 0.1, 0.0) < 0.15


def test_min_variance_with_perfect_negative_correlation_is_riskless():
    w = pf.min_variance_weight(0.2, 0.1, -1.0)
    assert pf.two_asset_volatility(w, 0.2, 0.1, -1.0) == pytest.approx(0, abs=1e-12)


def test_portfolio_variance_matches_two_asset_formula():
    cov = [[0.04, 0.006], [0.006, 0.01]]  # vols 0.2 / 0.1, correlation 0.3
    assert pf.portfolio_volatility([0.6, 0.4], cov) == pytest.approx(pf.two_asset_volatility(0.6, 0.2, 0.1, 0.3))


def test_beta_and_capm():
    market = [0.01, -0.02, 0.03, 0.015]
    asset = [2 * r for r in market]
    assert pf.beta(asset, market) == pytest.approx(2)
    assert pf.capm_expected_return(0.03, 1.2, 0.08) == pytest.approx(0.09)


def test_wacc():
    assert pf.wacc(600, 400, 0.10, 0.05, 0.25) == pytest.approx(0.075)
