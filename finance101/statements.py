"""Chapters 05-06 - Reading financial statements through ratios.

The income statement shows profit over a period, the balance sheet shows what
a company owns and owes at a point in time, and the cash flow statement shows
where cash actually went. Ratios make companies of different sizes comparable.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class IncomeStatement:
    revenue: float
    cost_of_goods_sold: float
    operating_expenses: float
    interest_expense: float
    tax_expense: float

    @property
    def gross_profit(self) -> float:
        return self.revenue - self.cost_of_goods_sold

    @property
    def operating_income(self) -> float:  # EBIT
        return self.gross_profit - self.operating_expenses

    @property
    def net_income(self) -> float:
        return self.operating_income - self.interest_expense - self.tax_expense


@dataclass
class BalanceSheet:
    current_assets: float
    inventory: float
    total_assets: float
    current_liabilities: float
    total_liabilities: float

    @property
    def equity(self) -> float:
        # The accounting identity: Assets = Liabilities + Equity
        return self.total_assets - self.total_liabilities


def profitability_ratios(inc: IncomeStatement, bal: BalanceSheet) -> Dict[str, float]:
    return {
        "gross_margin": inc.gross_profit / inc.revenue,
        "operating_margin": inc.operating_income / inc.revenue,
        "net_margin": inc.net_income / inc.revenue,
        "return_on_assets": inc.net_income / bal.total_assets,
        "return_on_equity": inc.net_income / bal.equity,
    }


def liquidity_ratios(bal: BalanceSheet) -> Dict[str, float]:
    return {
        "current_ratio": bal.current_assets / bal.current_liabilities,
        "quick_ratio": (bal.current_assets - bal.inventory) / bal.current_liabilities,
    }


def leverage_ratios(inc: IncomeStatement, bal: BalanceSheet) -> Dict[str, float]:
    return {
        "debt_to_equity": bal.total_liabilities / bal.equity,
        "debt_to_assets": bal.total_liabilities / bal.total_assets,
        "interest_coverage": inc.operating_income / inc.interest_expense,
    }


def dupont(inc: IncomeStatement, bal: BalanceSheet) -> Dict[str, float]:
    """ROE = net margin x asset turnover x equity multiplier."""
    net_margin = inc.net_income / inc.revenue
    asset_turnover = inc.revenue / bal.total_assets
    equity_multiplier = bal.total_assets / bal.equity
    return {
        "net_margin": net_margin,
        "asset_turnover": asset_turnover,
        "equity_multiplier": equity_multiplier,
        "return_on_equity": net_margin * asset_turnover * equity_multiplier,
    }
