"""Chapters 20 and 22 - Options, Black-Scholes and the Greeks.

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


def _norm_pdf(x: float) -> float:
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def greeks(spot: float, strike: float, years: float, rate: float, vol: float, kind: str = "call") -> dict:
    """Black-Scholes Greeks: sensitivities of the option price.

    delta -- per $1 move in the stock
    gamma -- change in delta per $1 move in the stock
    vega  -- per 1.00 (100 percentage points) change in volatility
    theta -- per year of time passing (divide by 365 for per day)
    rho   -- per 1.00 change in the interest rate
    """
    d1, d2 = _d1_d2(spot, strike, years, rate, vol)
    discount = math.exp(-rate * years)
    gamma = _norm_pdf(d1) / (spot * vol * math.sqrt(years))
    vega = spot * _norm_pdf(d1) * math.sqrt(years)
    common_theta = -spot * _norm_pdf(d1) * vol / (2 * math.sqrt(years))
    if kind == "call":
        delta = _norm_cdf(d1)
        theta = common_theta - rate * strike * discount * _norm_cdf(d2)
        rho = strike * years * discount * _norm_cdf(d2)
    elif kind == "put":
        delta = _norm_cdf(d1) - 1
        theta = common_theta + rate * strike * discount * _norm_cdf(-d2)
        rho = -strike * years * discount * _norm_cdf(-d2)
    else:
        raise ValueError("kind must be 'call' or 'put'")
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}


def implied_volatility(price: float, spot: float, strike: float, years: float, rate: float,
                       kind: str = "call", tol: float = 1e-8) -> float:
    """Volatility that makes Black-Scholes match a market price (bisection)."""
    pricer = black_scholes_call if kind == "call" else black_scholes_put
    low, high = 1e-6, 5.0
    for _ in range(200):
        mid = (low + high) / 2
        if pricer(spot, strike, years, rate, mid) > price:
            high = mid
        else:
            low = mid
        if high - low < tol:
            break
    return (low + high) / 2


def strategy_payoff(spot_at_expiry: float, legs) -> float:
    """Total payoff of a list of legs at expiry, ignoring premiums.

    Each leg is (kind, strike, quantity) with kind in {"call", "put", "stock"};
    quantity is negative for a short position. For "stock", strike is ignored.
    """
    total = 0.0
    for kind, strike, quantity in legs:
        if kind == "call":
            total += quantity * call_payoff(spot_at_expiry, strike)
        elif kind == "put":
            total += quantity * put_payoff(spot_at_expiry, strike)
        elif kind == "stock":
            total += quantity * spot_at_expiry
        else:
            raise ValueError(f"unknown leg kind {kind!r}")
    return total
