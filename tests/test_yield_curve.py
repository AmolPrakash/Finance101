import pytest

from finance101 import bonds, yield_curve as yc


def test_forward_rate():
    f = yc.forward_rate(0.03, 1, 0.04, 2)
    assert (1.03) * (1 + f) == pytest.approx(1.04 ** 2)


def test_flat_par_curve_gives_flat_spot_curve():
    assert yc.bootstrap_spot_rates([0.05] * 4) == pytest.approx([0.05] * 4)


def test_bootstrapped_curve_reprices_par_bonds():
    par = [0.02, 0.03, 0.035, 0.04]
    spots = yc.bootstrap_spot_rates(par)
    for n, c in enumerate(par, start=1):
        flows = [100 * c] * n
        flows[-1] += 100
        assert yc.price_from_spot_curve(flows, spots[:n]) == pytest.approx(100)


def test_flat_curve_matches_bond_price():
    flows = [5, 5, 105]
    assert yc.price_from_spot_curve(flows, [0.06] * 3) == pytest.approx(bonds.bond_price(100, 0.05, 0.06, 3, frequency=1))
