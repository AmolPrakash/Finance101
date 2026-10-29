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


def test_greeks_match_finite_differences():
    args = (100, 105, 0.75, 0.04, 0.3)
    g = opt.greeks(*args)
    h = 1e-4
    up = opt.black_scholes_call(100 + h, *args[1:])
    down = opt.black_scholes_call(100 - h, *args[1:])
    assert g["delta"] == pytest.approx((up - down) / (2 * h), rel=1e-5)
    assert g["gamma"] == pytest.approx((up - 2 * opt.black_scholes_call(*args) + down) / h ** 2, rel=1e-3)
    vega_fd = (opt.black_scholes_call(100, 105, 0.75, 0.04, 0.3 + h) - opt.black_scholes_call(100, 105, 0.75, 0.04, 0.3 - h)) / (2 * h)
    assert g["vega"] == pytest.approx(vega_fd, rel=1e-5)
    theta_fd = -(opt.black_scholes_call(100, 105, 0.75 + h, 0.04, 0.3) - opt.black_scholes_call(100, 105, 0.75 - h, 0.04, 0.3)) / (2 * h)
    assert g["theta"] == pytest.approx(theta_fd, rel=1e-5)
    put = opt.greeks(*args, kind="put")
    assert g["delta"] - put["delta"] == pytest.approx(1)


def test_implied_volatility_round_trip():
    price = opt.black_scholes_put(100, 90, 0.5, 0.03, 0.27)
    assert opt.implied_volatility(price, 100, 90, 0.5, 0.03, kind="put") == pytest.approx(0.27, abs=1e-6)


def test_strategy_payoff_straddle():
    straddle = [("call", 100, 1), ("put", 100, 1)]
    assert opt.strategy_payoff(80, straddle) == 20
    assert opt.strategy_payoff(115, straddle) == 15
    covered_call = [("stock", None, 1), ("call", 110, -1)]
    assert opt.strategy_payoff(130, covered_call) == 110
