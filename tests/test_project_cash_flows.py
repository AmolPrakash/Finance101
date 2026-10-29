import pytest

from finance101 import project_cash_flows as pcf


def test_operating_cash_flow_includes_tax_shield():
    # EBIT = 1000 - 400 - 200 = 400; after tax 300; plus depreciation 200
    assert pcf.operating_cash_flow(1000, 400, 200, 0.25) == pytest.approx(500)


def test_after_tax_salvage():
    assert pcf.after_tax_salvage(30, 20, 0.25) == pytest.approx(27.5)
    assert pcf.after_tax_salvage(10, 20, 0.25) == pytest.approx(12.5)


def test_free_cash_flow():
    assert pcf.free_cash_flow(400, 0.25, 200, 150, 50) == pytest.approx(300)


def test_project_cash_flows_recover_working_capital():
    flows = pcf.project_cash_flows(900, [1000] * 3, [400] * 3, life=3, tax_rate=0.25, salvage_value=100, nwc=50)
    assert flows[0] == -950
    assert flows[1] == pytest.approx(600 * 0.75 + 300 * 0.25)
    assert flows[3] == pytest.approx(flows[1] + 50 + 75)


def test_equivalent_annual_annuity():
    assert pcf.equivalent_annual_annuity(100, 0.10, 1) == pytest.approx(110)
