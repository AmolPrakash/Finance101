import pytest

from finance101 import loans


def test_mortgage_payment():
    # $200k, 30 years, 6% APR paid monthly
    assert loans.loan_payment(200_000, 0.06 / 12, 360) == pytest.approx(1199.10, abs=0.01)


def test_schedule_pays_off_loan():
    schedule = loans.amortization_schedule(10_000, 0.01, 12)
    assert len(schedule) == 12
    assert schedule[-1].balance == pytest.approx(0, abs=1e-6)
    assert sum(r.principal for r in schedule) == pytest.approx(10_000)
    assert schedule[0].interest > schedule[-1].interest


def test_total_interest():
    assert loans.total_interest(1200, 0, 12) == pytest.approx(0)
