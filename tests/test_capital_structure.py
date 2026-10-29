import pytest

from finance101 import capital_structure as cs


def test_mm_with_taxes():
    assert cs.levered_value(1000, 400, 0.25) == pytest.approx(1100)
    assert cs.cost_of_equity_levered(0.10, 0.05, 1.0) == pytest.approx(0.15)
    assert cs.cost_of_equity_levered(0.10, 0.05, 1.0, 0.2) == pytest.approx(0.14)


def test_beta_lever_unlever_round_trip():
    bl = cs.levered_beta(0.8, 0.5, 0.25)
    assert bl == pytest.approx(1.1)
    assert cs.unlevered_beta(bl, 0.5, 0.25) == pytest.approx(0.8)


def test_fair_buyback_keeps_price():
    price, shares = cs.share_price_after_buyback(1000, 100, 200)
    assert price == pytest.approx(10)
    assert shares == pytest.approx(80)
    assert cs.earnings_per_share(200, 40, 0.25, 80) == pytest.approx(1.5)
