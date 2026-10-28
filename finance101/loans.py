"""Lesson 03 - Loans and amortization.

A fully amortizing loan is just an annuity seen from the lender's side: the
borrower's level payments have a present value equal to the amount borrowed.
"""

from dataclasses import dataclass
from typing import List


def loan_payment(principal: float, rate: float, periods: int) -> float:
    """Level payment per period: PMT = P * r / [1 - (1 + r)^-n]"""
    if rate == 0:
        return principal / periods
    return principal * rate / (1 - (1 + rate) ** -periods)


@dataclass
class AmortizationRow:
    period: int
    payment: float
    interest: float
    principal: float
    balance: float


def amortization_schedule(principal: float, rate: float, periods: int) -> List[AmortizationRow]:
    """Break each payment into interest and principal.

    Early payments are mostly interest; later payments are mostly principal.
    """
    payment = loan_payment(principal, rate, periods)
    balance = principal
    rows = []
    for period in range(1, periods + 1):
        interest = balance * rate
        principal_paid = payment - interest
        balance -= principal_paid
        rows.append(AmortizationRow(period, payment, interest, principal_paid, max(balance, 0.0)))
    return rows


def total_interest(principal: float, rate: float, periods: int) -> float:
    """Total interest paid over the life of the loan."""
    return loan_payment(principal, rate, periods) * periods - principal
