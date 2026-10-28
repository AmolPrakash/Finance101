import pytest

from finance101.statements import BalanceSheet, IncomeStatement, dupont, liquidity_ratios, profitability_ratios


INC = IncomeStatement(revenue=1000, cost_of_goods_sold=600, operating_expenses=200, interest_expense=20, tax_expense=45)
BAL = BalanceSheet(current_assets=400, inventory=100, total_assets=1500, current_liabilities=200, total_liabilities=900)


def test_income_statement():
    assert INC.gross_profit == 400
    assert INC.operating_income == 200
    assert INC.net_income == 135


def test_ratios():
    assert profitability_ratios(INC, BAL)["return_on_equity"] == pytest.approx(135 / 600)
    assert liquidity_ratios(BAL)["quick_ratio"] == pytest.approx(1.5)


def test_dupont_reconciles_to_roe():
    d = dupont(INC, BAL)
    assert d["return_on_equity"] == pytest.approx(profitability_ratios(INC, BAL)["return_on_equity"])
