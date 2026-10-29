"""Chapter 02: How much is money worth across time?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import time_value as tv

print("$1,000 invested at 7% for 30 years grows to:", round(tv.future_value(1000, 0.07, 30), 2))
print("$1,000,000 in 40 years is worth today (at 7%):", round(tv.present_value(1_000_000, 0.07, 40), 2))
print("Saving $500/month for 30 years at 7%/yr (monthly):",
      round(tv.future_value_annuity(500, 0.07 / 12, 360), 2))
print("A 24% APR credit card compounded monthly really costs:", f"{tv.effective_annual_rate(0.24, 12):.2%}")
print("Rule of 72 at 9%:", tv.rule_of_72(0.09), "years vs exact", round(tv.years_to_double(0.09), 2))
print("8% nominal with 3% inflation is a real return of:", f"{tv.real_rate(0.08, 0.03):.2%}")

print("\nCompounding frequency matters ($10,000 at 10% for 10 years):")
for label, m in [("annual", 1), ("monthly", 12), ("daily", 365)]:
    print(f"  {label:>10}: {10_000 * (1 + tv.effective_annual_rate(0.10, m)) ** 10:,.2f}")
print(f"  {'continuous':>10}: {tv.future_value_continuous(10_000, 0.10, 10):,.2f}")
