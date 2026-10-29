# Annuities, Perpetuities and Loans

Many financial contracts pay the **same amount every period**: rent, salaries, mortgage payments, bond coupons, pension income. A level stream of payments is called an **annuity**, and one that never ends is a **perpetuity**. Adding up dozens or hundreds of discounted payments one by one would be tedious, but they have neat closed-form formulas. With them you can price a mortgage, plan retirement, or value a stock.

> [!IMPORTANT]
> A loan *is* an annuity. The bank gives you its present value today, and you pay it back in level installments. Once you understand annuities, you understand every mortgage, car loan and student loan.

## Ordinary annuities

An **ordinary annuity** pays \(PMT\) at the **end** of each of \(n\) periods. Its present value is

\[ PV = PMT \times \frac{1 - (1 + r)^{-n}}{r} \]

and its future value (at the time of the last payment) is

\[ FV = PMT \times \frac{(1 + r)^{n} - 1}{r} \]

Check the formula against brute-force discounting:

```python run
from finance101 import time_value as tv

pmt, r, n = 1_000, 0.06, 10
brute_force = sum(pmt / (1 + r) ** t for t in range(1, n + 1))
formula = tv.present_value_annuity(pmt, r, n)
print(f"Brute force: {brute_force:,.4f}")
print(f"Formula    : {formula:,.4f}")
```

### Where the formula comes from

An annuity is the difference between two perpetuities. One starts paying now and lasts forever; the other starts at year \(n+1\) and also lasts forever. Subtracting leaves exactly \(n\) payments. That's why both perpetuities and annuities share the \(PMT / r\) term:

\[ PV_{\text{annuity}} = \frac{PMT}{r} - \frac{PMT}{r}\cdot\frac{1}{(1+r)^n} \]

### Annuities due

If payments come at the **start** of each period (rent, insurance premiums, lease payments), each one is received one period earlier, so the annuity is worth \((1 + r)\) times more:

```python run
print(f"Ordinary annuity: {tv.present_value_annuity(1000, 0.06, 10):,.2f}")
print(f"Annuity due     : {tv.present_value_annuity(1000, 0.06, 10, due=True):,.2f}")
```

## Perpetuities

A perpetuity pays forever. Even infinitely many payments have a finite value, because far-off payments are discounted to almost nothing:

\[ PV = \frac{PMT}{r} \qquad\text{and with growth } g < r:\qquad PV = \frac{PMT_1}{r - g} \]

The growing perpetuity is the heart of the **dividend discount model** for stocks (Chapter 11) and the **terminal value** in company valuations.

```python run
# A charity wants to fund a $50,000 scholarship every year, forever, starting next year.
print(f"Endowment needed at 4%: ${tv.present_value_perpetuity(50_000, 0.04):,.0f}")

# ...and if the scholarship should grow 2% a year with tuition:
print(f"Growing with 2% inflation: ${tv.present_value_perpetuity(50_000, 0.04, growth=0.02):,.0f}")
```

### Growing annuities

A **growing annuity** has \(n\) payments growing at rate \(g\), like a salary or retirement income that rises with inflation:

\[ PV = \frac{PMT_1}{r - g}\left[1 - \left(\frac{1 + g}{1 + r}\right)^n\right] \]

```python run
def pv_growing_annuity(first_payment, rate, growth, periods):
    return first_payment / (rate - growth) * (1 - ((1 + growth) / (1 + rate)) ** periods)

# Lifetime earnings: $55,000 starting salary, 3% raises, 40-year career, 5% discount rate
print(f"PV of a career's earnings: ${pv_growing_annuity(55_000, 0.05, 0.03, 40):,.0f}")
```

You are, in present-value terms, probably a multi-million-dollar asset. That's one reason education is such a large financial decision.

## Loans and amortization

To find the payment on a loan, solve the annuity formula for \(PMT\):

\[ PMT = \frac{P \times r}{1 - (1 + r)^{-n}} \]

```python run
from finance101 import loans

principal = 350_000
apr = 0.065
years = 30
r = apr / 12            # mortgages quote an APR compounded monthly
n = years * 12

payment = loans.loan_payment(principal, r, n)
print(f"Monthly payment: ${payment:,.2f}")
print(f"Total paid     : ${payment * n:,.2f}")
print(f"Total interest : ${loans.total_interest(principal, r, n):,.2f}")
```

### The amortization schedule

Each payment first covers the interest on the outstanding balance; whatever is left reduces the principal. Early on, the balance is large, so most of the payment is interest.

```python run
schedule = loans.amortization_schedule(principal, r, n)

print(f"{'Month':>5} {'Payment':>10} {'Interest':>10} {'Principal':>10} {'Balance':>12}")
for row in schedule[:3] + schedule[178:181] + schedule[-3:]:
    print(f"{row.period:>5} {row.payment:>10,.2f} {row.interest:>10,.2f} {row.principal:>10,.2f} {row.balance:>12,.2f}")
```

```python run
import matplotlib.pyplot as plt

months = [row.period for row in schedule]
plt.stackplot(months, [row.interest for row in schedule], [row.principal for row in schedule],
              labels=["Interest", "Principal"], alpha=0.85)
plt.title("Where each mortgage payment goes")
plt.xlabel("Month"); plt.ylabel("$ per payment")
plt.legend(loc="upper left"); plt.margins(0, 0)
plt.show()

halfway = next(row.period for row in schedule if row.balance <= principal / 2)
print(f"You owe half the original balance only after month {halfway} ({halfway / 12:.1f} years).")
```

### The power of extra payments

Because interest is charged on the outstanding balance, paying extra principal early saves a lot of interest:

```python run
def payoff_with_extra(principal, rate, periods, extra):
    """Months to repay and total interest when paying `extra` on top of the regular payment."""
    payment = loans.loan_payment(principal, rate, periods)
    balance, month, interest_paid = principal, 0, 0.0
    while balance > 0.005:
        month += 1
        interest = balance * rate
        interest_paid += interest
        balance -= min(payment + extra - interest, balance)
    return month, interest_paid

for extra in [0, 100, 250, 500]:
    months_needed, interest = payoff_with_extra(principal, r, n, extra)
    print(f"Extra ${extra:>3}/month: paid off in {months_needed / 12:4.1f} years, interest ${interest:,.0f}")
```

## Worked example: 0% financing or cash back?

A car costs $32,000. The dealer offers either **0% financing for 60 months** or **$3,000 cash back**. If you take the cash back, you'd finance $29,000 with your credit union at 5.9% APR for 60 months.

Both loans last 60 months, so compare the monthly payments: the smaller payment is the better deal.

```python run
pay_zero = 32_000 / 60
pay_bank = loans.loan_payment(29_000, 0.059 / 12, 60)
print(f"0% dealer financing : ${pay_zero:,.2f}/month")
print(f"Cash back + bank loan: ${pay_bank:,.2f}/month")
print("Better deal:", "cash back" if pay_bank < pay_zero else "0% financing")
```

## Key takeaways

- **Annuity:** \(PV = PMT\frac{1-(1+r)^{-n}}{r}\). **Perpetuity:** \(PV = PMT/r\). **Growing perpetuity:** \(PMT_1/(r-g)\).
- An **annuity due** is worth \((1 + r)\) times an ordinary annuity.
- A loan payment is the annuity formula solved for \(PMT\); each payment splits into interest and principal.
- Interest dominates early payments; extra principal payments early in a loan save the most.

## Exercises

1. You can afford $2,200 a month for a 30-year mortgage at 6.75% APR. How large a loan can you take?
2. A lottery offers $1 million today or $60,000 a year for 25 years (first payment today). At 5%, which is worth more?
3. A share of preferred stock pays a fixed $5 dividend per year forever. If investors require 6.5%, what is it worth?
4. Make a 15-year version of the mortgage above. How much interest does it save compared with 30 years?

<details>
<summary>Solutions</summary>

```python run
print(f"1. Max loan: ${tv.present_value_annuity(2_200, 0.0675 / 12, 360):,.0f}")
print(f"2. Annuity due PV: ${tv.present_value_annuity(60_000, 0.05, 25, due=True):,.0f}  vs $1,000,000 → take the lump sum")
print(f"3. Preferred stock: ${tv.present_value_perpetuity(5, 0.065):.2f}")
saving = loans.total_interest(principal, r, 360) - loans.total_interest(principal, r, 180)
print(f"4. 15-year payment ${loans.loan_payment(principal, r, 180):,.2f}; interest saved ${saving:,.0f}")
```

</details>

## Watch & read

- [watch] [Khan Academy: Housing (mortgages, renting vs. buying)](https://www.khanacademy.org/economics-finance-domain/core-finance/housing). How mortgages work, with worked examples.
- [watch] [MIT 15.401 Finance Theory I](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/). The "Present Value Relations" lectures derive the annuity and perpetuity formulas.
- [read] [OpenStax *Principles of Finance*, Chapter 8: Time Value of Money II: Equal Multiple Payments](https://openstax.org/details/books/principles-finance). Annuities, perpetuities and loan amortization with practice problems.
- [read] [Investopedia: Annuity](https://www.investopedia.com/terms/a/annuity.asp) and [Amortization](https://www.investopedia.com/terms/a/amortization.asp). Quick references.
- [tool] [Consumer Financial Protection Bureau: Owning a home](https://www.consumerfinance.gov/owning-a-home/). Free, unbiased tools for comparing real mortgage offers.
