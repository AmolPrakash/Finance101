"""Chapter 23: Monte Carlo option pricing and Value at Risk."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import options, simulation

price, se = simulation.monte_carlo_option(100, 100, 1, 0.05, 0.2, simulations=50_000, seed=1)
print(f"Monte Carlo call: {price:.4f} ± {1.96 * se:.4f}  (Black-Scholes {options.black_scholes_call(100, 100, 1, 0.05, 0.2):.4f})")

var, es = simulation.monte_carlo_var(1_000_000, 0.07, 0.18, 1 / 12, confidence=0.99, simulations=50_000, seed=2)
print(f"1-month 99% VaR on $1m: ${var:,.0f}; expected shortfall ${es:,.0f}")

outcomes = sorted(simulation.retirement_simulation(0, 12_000, 30, 0.07, 0.15, simulations=2_000, seed=3))
print(f"Saving $12k/yr for 30 years: 10th pct ${outcomes[200]:,.0f}, median ${outcomes[1000]:,.0f}, 90th pct ${outcomes[1800]:,.0f}")
