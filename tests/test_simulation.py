import random
import statistics

import pytest

from finance101 import options as opt
from finance101 import simulation as sim


def test_gbm_path_shape():
    path = sim.gbm_path(100, 0.05, 0.2, 1, 252, rng=random.Random(1))
    assert len(path) == 253
    assert path[0] == 100
    assert all(p > 0 for p in path)


def test_monte_carlo_matches_black_scholes():
    price, se = sim.monte_carlo_option(100, 100, 1, 0.05, 0.2, simulations=50_000, seed=7)
    assert price == pytest.approx(opt.black_scholes_call(100, 100, 1, 0.05, 0.2), abs=4 * se)


def test_monte_carlo_var():
    var, es = sim.monte_carlo_var(1_000_000, 0.0, 0.2, 1 / 252, simulations=20_000, seed=3)
    assert 15_000 < var < 26_000  # roughly 1.645 * 0.2 / sqrt(252) * 1m = 20.7k
    assert es > var


def test_retirement_simulation_is_reproducible():
    a = sim.retirement_simulation(0, 10_000, 10, 0.06, 0.15, simulations=200, seed=1)
    b = sim.retirement_simulation(0, 10_000, 10, 0.06, 0.15, simulations=200, seed=1)
    assert a == b
    assert statistics.median(a) > 100_000
