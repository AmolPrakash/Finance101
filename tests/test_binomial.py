import pytest

from finance101 import binomial as b
from finance101 import options as opt


def test_converges_to_black_scholes():
    assert b.binomial_option(100, 100, 1, 0.05, 0.2, steps=500) == pytest.approx(10.4506, abs=0.01)
    assert b.binomial_option(100, 100, 1, 0.05, 0.2, steps=500, kind="put") == pytest.approx(5.5735, abs=0.01)


def test_american_put_worth_at_least_european():
    euro = b.binomial_option(100, 110, 1, 0.08, 0.2, steps=200, kind="put")
    amer = b.binomial_option(100, 110, 1, 0.08, 0.2, steps=200, kind="put", american=True)
    assert amer > euro


def test_american_call_without_dividends_equals_european():
    euro = b.binomial_option(100, 100, 1, 0.05, 0.2, steps=200)
    amer = b.binomial_option(100, 100, 1, 0.05, 0.2, steps=200, american=True)
    assert amer == pytest.approx(euro)


def test_one_step_replication_matches_risk_neutral_price():
    delta, bond, value = b.one_step_replication(100, 120, 80, 100, 0.0, 1)
    assert delta == pytest.approx(0.5)
    assert value == pytest.approx(10)
    assert opt.call_payoff(120, 100) == pytest.approx(delta * 120 + bond)
