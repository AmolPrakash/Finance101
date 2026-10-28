# 03 · Loans & Amortization

**Big idea:** a loan is an annuity. The level payment is chosen so that the present value of all payments equals the amount borrowed.

## Key concepts
| Concept | Formula | Code |
|---|---|---|
| Payment | `PMT = P × r / [1 − (1 + r)^−n]` | `loans.loan_payment` |
| Interest in a period | `balance × r` | `loans.amortization_schedule` |
| Principal in a period | `PMT − interest` | `loans.amortization_schedule` |

## Intuition
- Early payments are mostly interest because the balance is large.
- Shorter terms mean higher payments but dramatically less total interest.
- Extra principal payments early in a loan save the most interest.

## Run it
```bash
python examples/03_loans_and_amortization.py
```

## Exercises
1. Add an `extra_payment` parameter to the schedule. How many months does an extra $200/month save on the example mortgage?
2. A car dealer offers 0% APR or $3,000 cash back on a $30,000 car. With a 6% bank loan for 5 years, which deal wins?
