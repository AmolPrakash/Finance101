import math

import pytest

from finance101 import derivatives as d


def test_forward_price_cost_of_carry():
    assert d.forward_price(100, 0.05, 1) == pytest.approx(100 * math.exp(0.05))
    assert d.forward_price(100, 0.05, 1, income_yield=0.05) == pytest.approx(100)


def test_new_forward_is_worth_zero():
    f = d.forward_price(100, 0.04, 0.5, income_yield=0.01)
    assert d.forward_contract_value(100, f, 0.04, 0.5, income_yield=0.01) == pytest.approx(0, abs=1e-12)


def test_fx_forward_parity():
    # Higher domestic rate -> foreign currency trades at a forward premium
    assert d.fx_forward(1.10, 0.05, 0.02, 1) > 1.10


def test_futures_and_hedge():
    assert d.futures_pnl(4000, 4050, 2, 50) == 5000
    assert d.hedge_ratio(0.2, 0.25, 0.9) == pytest.approx(0.72)


def test_par_swap_is_worth_zero():
    dfs = [1 / 1.03, 1 / 1.035 ** 2, 1 / 1.04 ** 3]
    rate = d.par_swap_rate(dfs)
    assert d.swap_value_receive_fixed(1_000_000, rate, dfs) == pytest.approx(0, abs=1e-6)
    assert d.swap_value_receive_fixed(1_000_000, rate + 0.01, dfs) > 0
