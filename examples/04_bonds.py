"""Chapter 10: Bond prices, yields, and interest-rate risk."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import bonds

face, coupon, years = 1000, 0.05, 10
print("Price of a 10-year 5% coupon bond at different yields:")
for y in [0.03, 0.04, 0.05, 0.06, 0.07]:
    print(f"  YTM {y:.0%}: {bonds.bond_price(face, coupon, y, years):>9,.2f}")

price = 950
print(f"\nIf it trades at {price}, its YTM is {bonds.yield_to_maturity(price, face, coupon, years):.3%}")
print(f"Current yield: {bonds.current_yield(price, face, coupon):.3%}")

print("\nLonger bonds are riskier -- duration at 5% yield:")
for y in [2, 5, 10, 30]:
    print(f"  {y:>2}-year: Macaulay {bonds.macaulay_duration(face, coupon, 0.05, y):5.2f}, "
          f"modified {bonds.modified_duration(face, coupon, 0.05, y):5.2f}")
