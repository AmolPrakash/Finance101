import pytest

from finance101 import time_value as tv


def test_future_and_present_value_are_inverses():
    assert tv.future_value(100, 0.05, 10) == pytest.approx(162.889, abs=1e-3)
    assert tv.present_value(162.889, 0.05, 10) == pytest.approx(100, abs=1e-3)


def test_effective_annual_rate():
    assert tv.effective_annual_rate(0.12, 12) == pytest.approx(0.126825, abs=1e-6)


def test_annuities():
    assert tv.present_value_annuity(100, 0.05, 10) == pytest.approx(772.173, abs=1e-3)
    assert tv.future_value_annuity(100, 0.05, 10) == pytest.approx(1257.789, abs=1e-3)
    assert tv.present_value_annuity(100, 0.05, 10, due=True) == pytest.approx(772.173 * 1.05, abs=1e-3)
    assert tv.present_value_annuity(100, 0, 10) == 1000


def test_perpetuity():
    assert tv.present_value_perpetuity(5, 0.10) == pytest.approx(50)
    assert tv.present_value_perpetuity(5, 0.10, growth=0.05) == pytest.approx(100)
    with pytest.raises(ValueError):
        tv.present_value_perpetuity(5, 0.05, growth=0.05)


def test_doubling():
    assert tv.rule_of_72(0.08) == pytest.approx(9)
    assert tv.years_to_double(0.08) == pytest.approx(9.006, abs=1e-3)


def test_real_rate():
    assert tv.real_rate(0.08, 0.03) == pytest.approx(0.048544, abs=1e-6)


def test_solvers_invert_future_value():
    fv = tv.future_value(1000, 0.06, 12)
    assert tv.solve_rate(1000, fv, 12) == pytest.approx(0.06)
    assert tv.solve_periods(1000, fv, 0.06) == pytest.approx(12)


def test_annuity_payment_for_goal():
    pmt = tv.annuity_payment_for_goal(100_000, 0.05, 20)
    assert tv.future_value_annuity(pmt, 0.05, 20) == pytest.approx(100_000)
