"""Chapter 09: Build a project's free cash flows and stress-test the NPV."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101 import capital_budgeting as cb
from finance101 import project_cash_flows as pcf


def project(units=8_000, price=600):
    revenues = [units * price] * 4
    costs = [units * 350 + 500_000] * 4
    return pcf.project_cash_flows(2_400_000, revenues, costs, life=4, tax_rate=0.25, salvage_value=300_000, nwc=250_000)


flows = project()
print("Free cash flows:", [f"{cf:,.0f}" for cf in flows])
print(f"NPV at 11%: {cb.npv(0.11, flows):,.0f}   IRR: {cb.irr(flows):.1%}")
print("\nSensitivity of NPV to price:")
for price in [540, 570, 600, 630, 660]:
    print(f"  price {price}: NPV {cb.npv(0.11, project(price=price)):>12,.0f}")
