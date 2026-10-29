"""Chapter 06: Turning financial statements into ratios."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

from finance101.statements import (BalanceSheet, IncomeStatement, dupont, leverage_ratios,
                                   liquidity_ratios, profitability_ratios)

inc = IncomeStatement(revenue=5_000, cost_of_goods_sold=3_000, operating_expenses=1_200,
                      interest_expense=100, tax_expense=150)
bal = BalanceSheet(current_assets=1_800, inventory=600, total_assets=6_000,
                   current_liabilities=1_000, total_liabilities=3_500)

print(f"Net income: {inc.net_income:,.0f}   Equity: {bal.equity:,.0f}\n")
for title, ratios in [("Profitability", profitability_ratios(inc, bal)),
                      ("Liquidity", liquidity_ratios(bal)),
                      ("Leverage", leverage_ratios(inc, bal)),
                      ("DuPont", dupont(inc, bal))]:
    print(title)
    for name, value in ratios.items():
        print(f"  {name:<18} {value:8.3f}")
