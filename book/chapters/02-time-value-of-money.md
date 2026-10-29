# The Time Value of Money

Would you rather have $1,000 today or $1,000 in five years? Today, obviously. You could invest it and have more than $1,000 in five years. Even if you just want to spend it, you get to spend it sooner, and there's no risk the promise is broken.

That simple preference is the **time value of money**, and it is the single most important idea in finance. Every valuation, from a savings account to a bond to an entire company, is an application of this chapter.

> [!IMPORTANT]
> Money at different dates is like money in different currencies. You can't add dollars-today to dollars-in-five-years any more than you can add dollars to euros. You must first convert them to the same date, and the exchange rate between dates is the **interest rate**.

## Compounding: moving money forward

Invest $1,000 at 10% a year. After one year you have $1,000 × 1.10 = $1,100. In year two you earn 10% on $1,100, not just on the original $1,000. That's **interest on interest**, or **compounding**.

After \(n\) periods at rate \(r\) per period, a present value \(PV\) grows to a future value:

\[ FV = PV \times (1 + r)^n \]

```python run
from finance101 import time_value as tv

pv = 1000
r = 0.10
for n in range(0, 6):
    print(f"Year {n}: ${tv.future_value(pv, r, n):>9,.2f}")
```

### Simple vs. compound interest

With **simple interest** you only ever earn interest on the original amount. The difference looks tiny at first and becomes enormous over long horizons:

```python run
import matplotlib.pyplot as plt

years = list(range(0, 51))
simple = [pv * (1 + r * n) for n in years]
compound = [tv.future_value(pv, r, n) for n in years]

plt.plot(years, compound, label="Compound interest")
plt.plot(years, simple, label="Simple interest", linestyle="--")
plt.title("$1,000 at 10% per year")
plt.xlabel("Years"); plt.ylabel("Value ($)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()

print(f"After 50 years: simple ${simple[-1]:,.0f} vs compound ${compound[-1]:,.0f}")
```

## Discounting: moving money backward

If compounding answers "what will this be worth later?", **discounting** answers "what is a future amount worth today?" Just rearrange the formula:

\[ PV = \frac{FV}{(1 + r)^n} \]

The term \(\frac{1}{(1+r)^n}\) is the **discount factor**: what $1 at time \(n\) is worth today.

```python run
# A relative promises you $10,000 when you graduate in 4 years.
# If you could earn 6% a year elsewhere, what is that promise worth today?
tv.present_value(10_000, 0.06, 4)
```

The interest rate used for discounting is called the **discount rate**, **required return** or **opportunity cost of capital**. It's the return you give up by not investing elsewhere at similar risk. Choosing it well is a big part of FIN 102.

### Watching discount factors decay

```python run
for rate in [0.02, 0.05, 0.10, 0.15]:
    factors = [1 / (1 + rate) ** n for n in (1, 5, 10, 20, 30)]
    print(f"{rate:>4.0%}: " + "  ".join(f"{f:.3f}" for f in factors))
print("        n=1    n=5    n=10   n=20   n=30")
```

At 15%, a dollar 30 years away is worth about 1.5 cents today. That is why high discount rates make long-term projects look unattractive, and why the choice of discount rate matters so much in climate, pension and infrastructure decisions.

## Timelines and multiple cash flows

Real problems involve several cash flows at different dates. Draw a **timeline**, convert each cash flow to the same date, then add.

```
Time:     0        1        2        3
         ─┼────────┼────────┼────────┼─
Cash:  -5,000    2,000    2,000    2,500
```

\[ PV = \sum_{t=0}^{n} \frac{CF_t}{(1 + r)^t} \]

```python run
cash_flows = [-5000, 2000, 2000, 2500]
rate = 0.08

total = 0
for t, cf in enumerate(cash_flows):
    pv_t = cf / (1 + rate) ** t
    total += pv_t
    print(f"t={t}: cash flow {cf:>7,}  →  PV {pv_t:>9,.2f}")
print(f"Sum of PVs (net present value): {total:,.2f}")
```

The sum is positive, so receiving those future cash flows is worth more than the $5,000 they cost, at 8%. You have just computed a **net present value (NPV)**, the main decision tool of Chapter 8.

## Solving for the rate or the time

Sometimes you know the values and want the **rate** or the **number of periods**.

\[ r = \left(\frac{FV}{PV}\right)^{1/n} - 1 \qquad n = \frac{\ln(FV / PV)}{\ln(1 + r)} \]

```python run
# A house bought for $180,000 sold 12 years later for $310,000. Annual growth?
print(f"Annual growth rate: {tv.solve_rate(180_000, 310_000, 12):.2%}")

# How long to turn $5,000 into $20,000 at 7%?
print(f"Years needed: {tv.solve_periods(5_000, 20_000, 0.07):.1f}")
```

### The Rule of 72

A handy mental shortcut: money doubles in roughly **72 ÷ (interest rate in %)** years.

```python run
for rate in [0.02, 0.04, 0.06, 0.08, 0.12, 0.24]:
    print(f"{rate:>4.0%}: rule of 72 says {tv.rule_of_72(rate):5.1f} years, exact {tv.years_to_double(rate):5.2f}")
```

The rule works best for rates between about 5% and 12%.

## Worked example: which offer is better?

You win a contest and can choose:

- **A:** $50,000 today
- **B:** $15,000 a year for 4 years, starting one year from now
- **C:** $65,000 in 3 years

At a 7% discount rate, convert everything to today's dollars:

```python run
rate = 0.07
offers = {
    "A: $50k now": 50_000,
    "B: $15k x 4 years": sum(tv.present_value(15_000, rate, t) for t in range(1, 5)),
    "C: $65k in 3 years": tv.present_value(65_000, rate, 3),
}
for name, value in sorted(offers.items(), key=lambda kv: -kv[1]):
    print(f"{name:<20} PV = ${value:,.0f}")
```

> [!TIP]
> Change `rate` to 3% and then to 12%. The ranking changes. The best choice depends on your opportunity cost. If you have expensive credit card debt (a high "rate"), money now is worth much more to you.

## Key takeaways

- **Compounding** moves money forward: \(FV = PV(1+r)^n\). **Discounting** moves it back: \(PV = FV/(1+r)^n\).
- Only add or compare cash flows **at the same date**.
- The discount rate is an **opportunity cost**: the return on the best alternative of similar risk.
- Small differences in rates and long horizons create enormous differences in value.

## Exercises

1. You want $40,000 for a car in 6 years. How much must you invest today at 5%?
2. Your grandparents bought a stamp collection for $500 in 1975. It's worth $9,000 in 2025. What annual return did it earn?
3. At 9%, roughly how long until an investment triples? Use `solve_periods`.
4. Would you rather have $1,000 today or $1,500 in 5 years if your opportunity cost is 10%? At what rate are you indifferent?

<details>
<summary>Solutions</summary>

```python run
print(f"1. Invest today: ${tv.present_value(40_000, 0.05, 6):,.2f}")
print(f"2. Annual return: {tv.solve_rate(500, 9_000, 50):.2%}")
print(f"3. Years to triple at 9%: {tv.solve_periods(1, 3, 0.09):.1f}")
print(f"4. PV of $1,500 at 10%: ${tv.present_value(1500, 0.10, 5):,.2f}  → take the $1,000 today")
print(f"   Indifference rate: {tv.solve_rate(1000, 1500, 5):.2%}")
```

</details>

## Watch & read

- [watch] [Khan Academy: Interest and debt](https://www.khanacademy.org/economics-finance-domain/core-finance/interest-tutorial). Compound interest, present value and the Rule of 72, step by step.
- [watch] [MIT 15.401 Finance Theory I (Andrew Lo)](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/). Lectures 2–4, "Present Value Relations", are a rigorous treatment with full video.
- [read] [OpenStax *Principles of Finance*, Chapter 7: Time Value of Money I](https://openstax.org/details/books/principles-finance). Free textbook chapter with practice problems.
- [read] [Investopedia: Time Value of Money](https://www.investopedia.com/terms/t/timevalueofmoney.asp). A concise reference with formulas.
- [tool] [Investor.gov compound interest calculator](https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator). The SEC's free calculator; check your answers against it.
