"""Chapter 23 - Monte Carlo simulation.

When a problem has no neat formula, simulate thousands of possible futures
and average. Pass a seed for reproducible results.
"""

import math
import random
import statistics
from typing import List, Optional


def gbm_path(spot: float, drift: float, vol: float, years: float, steps: int,
             rng: Optional[random.Random] = None) -> List[float]:
    """One geometric Brownian motion price path (the Black-Scholes stock model)."""
    rng = rng or random.Random()
    dt = years / steps
    prices = [spot]
    for _ in range(steps):
        shock = rng.gauss(0, 1)
        prices.append(prices[-1] * math.exp((drift - vol ** 2 / 2) * dt + vol * math.sqrt(dt) * shock))
    return prices


def monte_carlo_option(spot: float, strike: float, years: float, rate: float, vol: float,
                       simulations: int = 100_000, kind: str = "call", seed: Optional[int] = None):
    """Price a European option by simulating terminal prices under risk-neutral drift.

    Returns (price, standard_error).
    """
    rng = random.Random(seed)
    discount = math.exp(-rate * years)
    payoffs = []
    for _ in range(simulations):
        terminal = spot * math.exp((rate - vol ** 2 / 2) * years + vol * math.sqrt(years) * rng.gauss(0, 1))
        payoff = max(terminal - strike, 0.0) if kind == "call" else max(strike - terminal, 0.0)
        payoffs.append(discount * payoff)
    return statistics.mean(payoffs), statistics.stdev(payoffs) / math.sqrt(simulations)


def monte_carlo_var(value: float, mean: float, vol: float, horizon_years: float,
                    confidence: float = 0.95, simulations: int = 100_000, seed: Optional[int] = None):
    """Simulated Value at Risk and expected shortfall in currency units.

    Returns (var, expected_shortfall), both as positive losses.
    """
    rng = random.Random(seed)
    losses = sorted(
        value - value * math.exp((mean - vol ** 2 / 2) * horizon_years + vol * math.sqrt(horizon_years) * rng.gauss(0, 1))
        for _ in range(simulations)
    )
    index = int(confidence * simulations)
    return losses[index], statistics.mean(losses[index:])


def retirement_simulation(start_balance: float, annual_contribution: float, years: int,
                          mean_return: float, vol: float, simulations: int = 5_000,
                          seed: Optional[int] = None) -> List[float]:
    """Ending balances from random annual returns -- shows the range of outcomes, not one number."""
    rng = random.Random(seed)
    results = []
    for _ in range(simulations):
        balance = start_balance
        for _ in range(years):
            balance = balance * (1 + rng.gauss(mean_return, vol)) + annual_contribution
        results.append(balance)
    return results
