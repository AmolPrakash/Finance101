"""Chapters 19-22: Forwards, binomial trees, Black-Scholes and the Greeks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import binomial, derivatives, options

print(f"1-year forward on a $100 stock at 5%: {derivatives.forward_price(100, 0.05, 1):.2f}")

bs = options.black_scholes_call(100, 100, 1, 0.05, 0.2)
print(f"\nBlack-Scholes call: {bs:.4f}")
for steps in [10, 50, 250]:
    print(f"  binomial with {steps:>3} steps: {binomial.binomial_option(100, 100, 1, 0.05, 0.2, steps=steps):.4f}")

euro = binomial.binomial_option(100, 110, 1, 0.06, 0.25, steps=300, kind="put")
amer = binomial.binomial_option(100, 110, 1, 0.06, 0.25, steps=300, kind="put", american=True)
print(f"\nPut K=110: European {euro:.4f}, American {amer:.4f} (early-exercise premium {amer - euro:.4f})")

print("\nGreeks of a 6-month 105-strike call:")
for name, value in options.greeks(100, 105, 0.5, 0.04, 0.25).items():
    print(f"  {name:<6} {value:9.4f}")
print(f"Implied vol of a call trading at 7.50: {options.implied_volatility(7.50, 100, 100, 0.5, 0.04):.2%}")
