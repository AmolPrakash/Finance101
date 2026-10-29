"""Chapters 20-22: Option payoffs and Black-Scholes pricing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import options as opt

strike = 100
print("Payoff at expiry (strike 100):")
for s in [80, 90, 100, 110, 120]:
    print(f"  S={s:>3}: call {opt.call_payoff(s, strike):>5.1f}   put {opt.put_payoff(s, strike):>5.1f}")

spot, years, rate = 100, 0.5, 0.04
print("\nBlack-Scholes, 6 months, r=4%:")
for vol in [0.10, 0.20, 0.40]:
    call = opt.black_scholes_call(spot, strike, years, rate, vol)
    put = opt.black_scholes_put(spot, strike, years, rate, vol)
    print(f"  vol {vol:.0%}: call {call:6.2f}  put {put:6.2f}  delta {opt.call_delta(spot, strike, years, rate, vol):.2f}")
