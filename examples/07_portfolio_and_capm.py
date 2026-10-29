"""Chapters 15-16: Diversification and the price of risk."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import portfolio as pf

vol_stocks, vol_bonds = 0.18, 0.06
print("50/50 stock-bond portfolio volatility by correlation:")
for rho in [1.0, 0.5, 0.0, -0.5, -1.0]:
    print(f"  rho={rho:+.1f}: {pf.two_asset_volatility(0.5, vol_stocks, vol_bonds, rho):.2%}")

w = pf.min_variance_weight(vol_stocks, vol_bonds, 0.2)
print(f"\nMinimum-variance mix at rho=0.2: {w:.1%} stocks, {1 - w:.1%} bonds "
      f"(vol {pf.two_asset_volatility(w, vol_stocks, vol_bonds, 0.2):.2%})")

print("\nCAPM required returns (rf=4%, market=9%):")
for b in [0.5, 1.0, 1.5]:
    print(f"  beta {b}: {pf.capm_expected_return(0.04, b, 0.09):.2%}")

print(f"\nWACC (60% equity @ 10%, 40% debt @ 6%, 25% tax): {pf.wacc(60, 40, 0.10, 0.06, 0.25):.2%}")
