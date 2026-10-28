import pytest

from finance101 import capital_budgeting as cb


def test_npv():
    assert cb.npv(0.10, [-100, 60, 60]) == pytest.approx(4.1322, abs=1e-4)


def test_irr_makes_npv_zero():
    assert cb.irr([-100, 110]) == pytest.approx(0.10, abs=1e-8)
    flows = [-1000, 300, 400, 500, 200]
    assert cb.npv(cb.irr(flows), flows) == pytest.approx(0, abs=1e-6)


def test_payback():
    assert cb.payback_period([-100, 40, 40, 40]) == pytest.approx(2.5)
    assert cb.payback_period([-100, 10, 10]) is None
    assert cb.discounted_payback_period(0.10, [-100, 40, 40, 40]) is None


def test_profitability_index_matches_npv_sign():
    flows = [-100, 60, 60]
    assert cb.profitability_index(0.10, flows) == pytest.approx(1.041322, abs=1e-6)
