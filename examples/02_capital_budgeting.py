"""Lesson 02: Should we invest in this project?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import capital_budgeting as cb

projects = {
    "Fast payback": [-10_000, 6_000, 5_000, 1_000, 500],
    "Slow but big": [-10_000, 1_000, 2_000, 5_000, 9_000],
}
rate = 0.10
for name, flows in projects.items():
    print(f"{name}: {flows}")
    print(f"  NPV @ {rate:.0%}:       {cb.npv(rate, flows):>10,.2f}")
    print(f"  IRR:              {cb.irr(flows):>10.2%}")
    print(f"  Payback:          {cb.payback_period(flows):>10.2f} years")
    print(f"  Profitability idx:{cb.profitability_index(rate, flows):>10.3f}")

print("\nNPV profile -- how the discount rate changes the decision:")
for r in [0.0, 0.05, 0.10, 0.15, 0.20]:
    row = "  ".join(f"{name}: {cb.npv(r, f):>9,.0f}" for name, f in projects.items())
    print(f"  {r:>4.0%}  {row}")
