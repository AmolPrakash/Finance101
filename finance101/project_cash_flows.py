"""Chapter 09 - Project cash flows.

NPV is only as good as the cash flows you feed it. Projects are valued on
incremental, after-tax free cash flow -- not on accounting profit.
"""

from typing import List, Sequence


def straight_line_depreciation(cost: float, salvage: float, life: int) -> float:
    """Equal depreciation expense each year."""
    return (cost - salvage) / life


def operating_cash_flow(revenue: float, costs: float, depreciation: float, tax_rate: float) -> float:
    """OCF = (Revenue - Costs - Depreciation) x (1 - t) + Depreciation

    Depreciation is not a cash outflow, but it lowers taxes: the "tax shield".
    """
    ebit = revenue - costs - depreciation
    return ebit * (1 - tax_rate) + depreciation


def after_tax_salvage(sale_price: float, book_value: float, tax_rate: float) -> float:
    """Cash from selling an asset: gains are taxed, losses save tax."""
    return sale_price - tax_rate * (sale_price - book_value)


def free_cash_flow(ebit: float, tax_rate: float, depreciation: float, capex: float,
                   change_in_nwc: float) -> float:
    """FCF = EBIT(1 - t) + Depreciation - CapEx - Change in net working capital"""
    return ebit * (1 - tax_rate) + depreciation - capex - change_in_nwc


def project_cash_flows(investment: float, revenues: Sequence[float], costs: Sequence[float],
                       life: int, tax_rate: float, salvage_value: float = 0.0,
                       nwc: float = 0.0) -> List[float]:
    """Year-by-year free cash flows for a simple expansion project.

    The asset is depreciated straight-line to zero, net working capital
    ``nwc`` is invested at year 0 and recovered in the final year, and the
    asset is sold for ``salvage_value`` at the end.
    """
    depreciation = straight_line_depreciation(investment, 0.0, life)
    flows = [-investment - nwc]
    for year in range(life):
        flows.append(operating_cash_flow(revenues[year], costs[year], depreciation, tax_rate))
    flows[-1] += nwc + after_tax_salvage(salvage_value, 0.0, tax_rate)
    return flows


def equivalent_annual_annuity(npv_value: float, rate: float, life: int) -> float:
    """Spread an NPV evenly over a project's life to compare projects of unequal lives."""
    return npv_value * rate / (1 - (1 + rate) ** -life)
