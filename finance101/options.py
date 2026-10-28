"""Lesson 09 - Options.

A call is the right to buy at the strike price; a put is the right to sell.
Black-Scholes prices European options assuming log-normal stock prices.
"""

import math


def _norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def call_payoff(spot_at_expiry: float, strike: float) -> float:
    return max(spot_at_expiry - strike, 0.0)


def put_payoff(spot_at_expiry: float, strike: float) -> float:
    return max(strike - spot_at_expiry, 0.0)


def _d1_d2(spot: float, strike: float, years: float, rate: float, vol: float):
    d1 = (math.log(spot / strike) + (rate + vol ** 2 / 2) * years) / (vol * math.sqrt(years))
    return d1, d1 - vol * math.sqrt(years)


def black_scholes_call(spot: float, strike: float, years: float, rate: float, vol: float) -> float:
    """C = S N(d1) - K e^(-rT) N(d2)"""
    d1, d2 = _d1_d2(spot, strike, years, rate, vol)
    return spot * _norm_cdf(d1) - strike * math.exp(-rate * years) * _norm_cdf(d2)


def black_scholes_put(spot: float, strike: float, years: float, rate: float, vol: float) -> float:
    """P = K e^(-rT) N(-d2) - S N(-d1)"""
    d1, d2 = _d1_d2(spot, strike, years, rate, vol)
    return strike * math.exp(-rate * years) * _norm_cdf(-d2) - spot * _norm_cdf(-d1)


def put_call_parity_put(call_price: float, spot: float, strike: float, years: float, rate: float) -> float:
    """C - P = S - K e^(-rT), solved for P."""
    return call_price - spot + strike * math.exp(-rate * years)


def call_delta(spot: float, strike: float, years: float, rate: float, vol: float) -> float:
    """How much the call price moves per $1 move in the stock: N(d1)."""
    d1, _ = _d1_d2(spot, strike, years, rate, vol)
    return _norm_cdf(d1)
