"""Chapter 21 - Binomial option pricing.

Model the stock as moving up or down each step. At every node, an option can
be replicated with stock and a bond, so its value is the discounted
*risk-neutral* expected value of the next step.
"""

import math


def crr_parameters(vol: float, rate: float, dt: float):
    """Cox-Ross-Rubinstein up/down factors and risk-neutral up probability."""
    up = math.exp(vol * math.sqrt(dt))
    down = 1 / up
    p = (math.exp(rate * dt) - down) / (up - down)
    return up, down, p


def binomial_option(spot: float, strike: float, years: float, rate: float, vol: float,
                    steps: int = 100, kind: str = "call", american: bool = False) -> float:
    """Price a European or American option on a recombining binomial tree."""
    dt = years / steps
    up, down, p = crr_parameters(vol, rate, dt)
    discount = math.exp(-rate * dt)

    def exercise(price: float) -> float:
        return max(price - strike, 0.0) if kind == "call" else max(strike - price, 0.0)

    # Option values at expiry; node j has j up-moves.
    values = [exercise(spot * up ** j * down ** (steps - j)) for j in range(steps + 1)]
    for step in range(steps - 1, -1, -1):
        for j in range(step + 1):
            continuation = discount * (p * values[j + 1] + (1 - p) * values[j])
            if american:
                continuation = max(continuation, exercise(spot * up ** j * down ** (step - j)))
            values[j] = continuation
    return values[0]


def one_step_replication(spot: float, up_price: float, down_price: float, strike: float,
                         rate: float, years: float, kind: str = "call"):
    """Replicate an option with ``delta`` shares and a ``bond`` position.

    Returns (delta, bond, option_value).
    """
    payoff = (lambda s: max(s - strike, 0.0)) if kind == "call" else (lambda s: max(strike - s, 0.0))
    v_up, v_down = payoff(up_price), payoff(down_price)
    delta = (v_up - v_down) / (up_price - down_price)
    bond = (v_up - delta * up_price) * math.exp(-rate * years)
    return delta, bond, delta * spot + bond
