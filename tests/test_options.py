import pytest

from finance101 import options as opt


def test_payoffs():
    assert opt.call_payoff(110, 100) == 10
    assert opt.put_payoff(110, 100) == 0


def test_black_scholes_textbook_values():
    assert opt.black_scholes_call(100, 100, 1, 0.05, 0.2) == pytest.approx(10.4506, abs=1e-4)
    assert opt.black_scholes_put(100, 100, 1, 0.05, 0.2) == pytest.approx(5.5735, abs=1e-4)


def test_put_call_parity():
    call = opt.black_scholes_call(100, 95, 0.5, 0.03, 0.25)
    put = opt.black_scholes_put(100, 95, 0.5, 0.03, 0.25)
    assert opt.put_call_parity_put(call, 100, 95, 0.5, 0.03) == pytest.approx(put)
    assert 0 < opt.call_delta(100, 95, 0.5, 0.03, 0.25) < 1
