"""Chapter 11: What is a share of stock worth?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import equity

print("Gordon growth: D1=$2.00, r=9%, g=4% ->", round(equity.gordon_growth_value(2.00, 0.09, 0.04), 2))
print("Sensitivity to the growth assumption:")
for g in [0.02, 0.04, 0.06, 0.08]:
    print(f"  g={g:.0%}: {equity.gordon_growth_value(2.00, 0.09, g):>8.2f}")

print("\nTwo-stage: D0=$1, 15% growth for 5 yrs then 3%, r=10% ->",
      round(equity.two_stage_ddm(1.00, 0.10, 0.15, 5, 0.03), 2))
print("DCF of FCFs [100, 120, 140] with 8% discount and 2% terminal growth ->",
      round(equity.dcf_value([100, 120, 140], 0.08, 0.02), 2))
