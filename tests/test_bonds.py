import pytest

from finance101 import bonds


def test_par_bond_prices_at_face():
    assert bonds.bond_price(1000, 0.05, 0.05, 10) == pytest.approx(1000)


def test_price_yield_inverse_relationship():
    assert bonds.bond_price(1000, 0.05, 0.06, 10) < 1000 < bonds.bond_price(1000, 0.05, 0.04, 10)


def test_ytm_round_trip():
    price = bonds.bond_price(1000, 0.06, 0.072, 7)
    assert bonds.yield_to_maturity(price, 1000, 0.06, 7) == pytest.approx(0.072, abs=1e-8)


def test_zero_coupon_duration_equals_maturity():
    assert bonds.macaulay_duration(1000, 0.0, 0.05, 10, frequency=1) == pytest.approx(10)


def test_duration_approximates_price_change():
    base = bonds.bond_price(1000, 0.05, 0.05, 10)
    bumped = bonds.bond_price(1000, 0.05, 0.0501, 10)
    mod_dur = bonds.modified_duration(1000, 0.05, 0.05, 10)
    assert (bumped - base) / base == pytest.approx(-mod_dur * 0.0001, rel=1e-3)
    assert bonds.convexity(1000, 0.05, 0.05, 10) > 0


def test_current_yield():
    assert bonds.current_yield(950, 1000, 0.05) == pytest.approx(50 / 950)
