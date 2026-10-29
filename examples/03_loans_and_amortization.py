"""Chapter 04: Where does a mortgage payment actually go?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import loans

principal, apr, years = 300_000, 0.065, 30
rate, n = apr / 12, years * 12
schedule = loans.amortization_schedule(principal, rate, n)

print(f"Monthly payment: {loans.loan_payment(principal, rate, n):,.2f}")
print(f"Total interest over {years} years: {loans.total_interest(principal, rate, n):,.2f}\n")
print(f"{'Month':>5} {'Payment':>10} {'Interest':>10} {'Principal':>10} {'Balance':>12}")
for row in schedule[:3] + schedule[-3:]:
    print(f"{row.period:>5} {row.payment:>10,.2f} {row.interest:>10,.2f} {row.principal:>10,.2f} {row.balance:>12,.2f}")

print("\n15-year vs 30-year total interest:")
for y in (15, 30):
    print(f"  {y} years: {loans.total_interest(principal, rate, y * 12):,.0f}")
