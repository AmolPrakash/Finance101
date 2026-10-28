import pytest

from finance101 import equity


def test_gordon_growth():
    assert equity.gordon_growth_value(2, 0.10, 0.05) == pytest.approx(40)
    assert equity.implied_required_return(40, 2, 0.05) == pytest.approx(0.10)


def test_two_stage_reduces_to_gordon_when_growth_equal():
    two_stage = equity.two_stage_ddm(2, 0.10, 0.05, 5, 0.05)
    assert two_stage == pytest.approx(equity.gordon_growth_value(2 * 1.05, 0.10, 0.05))


def test_dcf_positive():
    assert equity.dcf_value([100, 110, 120], 0.09, 0.02) > 0
