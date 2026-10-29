"""Chapter 17: Bootstrap a spot curve, then measure interest-rate risk."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import bonds
from finance101 import yield_curve as yc

par = [0.040, 0.043, 0.045, 0.047, 0.048]
spots = yc.bootstrap_spot_rates(par)
print("Maturity  par     spot    1y forward")
for t, (p, s) in enumerate(zip(par, spots), start=1):
    fwd = s if t == 1 else yc.forward_rate(spots[t - 2], t - 1, s, t)
    print(f"{t:>8}  {p:.3%}  {s:.3%}  {fwd:.3%}")

print("\nDuration and convexity at a 5% yield:")
for years in [2, 10, 30]:
    print(f"  {years:>2}-year 5% bond: modified duration {bonds.modified_duration(1000, 0.05, 0.05, years):5.2f}, "
          f"convexity {bonds.convexity(1000, 0.05, 0.05, years):7.1f}")
