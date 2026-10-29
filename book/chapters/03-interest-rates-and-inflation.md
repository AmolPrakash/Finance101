# Interest Rates, Compounding and Inflation

Chapter 2 treated "the interest rate" as one simple number. In practice, rates are quoted in confusing ways, compounded at different frequencies, and eroded by inflation. A credit card advertising "24% APR" actually costs more than 24% a year. A savings account paying 4% may still be losing you purchasing power. This chapter teaches you to see through the quotes.

> [!IMPORTANT]
> Always ask two questions about any rate: **How often does it compound?** and **Is it nominal or real?** Only compare rates once they are on the same basis.

## Compounding frequency: APR vs. EAR

Lenders often quote an **annual percentage rate (APR)**, also called the *nominal* or *stated* rate. If interest compounds \(m\) times a year, the rate per period is \(APR / m\). Because of interest-on-interest within the year, the true annual growth is higher. That true rate is the **effective annual rate (EAR)**:

\[ EAR = \left(1 + \frac{APR}{m}\right)^m - 1 \]

```python run
from finance101 import time_value as tv

apr = 0.24   # a typical credit card
for label, m in [("annually", 1), ("semi-annually", 2), ("quarterly", 4), ("monthly", 12), ("daily", 365)]:
    print(f"24% APR compounded {label:<14}: EAR = {tv.effective_annual_rate(apr, m):.3%}")
```

> [!WARNING]
> In the US, lenders must disclose the APR, but the APR ignores compounding. Savings accounts often advertise the **APY** (annual percentage yield), which *is* the effective rate. Compare EARs, never an APR with an APY.

### Continuous compounding

What happens as compounding becomes infinitely frequent? The limit is **continuous compounding**:

\[ FV = PV \times e^{r t} \qquad EAR = e^{r} - 1 \]

```python run
import math

pv, r, years = 10_000, 0.10, 10
for m in [1, 4, 12, 365, 10_000]:
    fv = pv * (1 + r / m) ** (m * years)
    print(f"m = {m:>6}: ${fv:,.2f}")
print(f"continuous: ${tv.future_value_continuous(pv, r, years):,.2f}   (e^(r·t) = {math.exp(r * years):.5f})")
```

Continuous compounding shows up constantly in derivatives pricing (FIN 202) because it makes the math cleaner: growth rates simply add.

### Converting a rate to any period

To convert an effective annual rate into an equivalent monthly rate (or any other period), use roots, not division:

\[ r_{\text{monthly}} = (1 + EAR)^{1/12} - 1 \]

```python run
ear = 0.06
monthly = (1 + ear) ** (1 / 12) - 1
print(f"Equivalent monthly rate: {monthly:.4%}  (not 6%/12 = {0.06/12:.4%})")
print(f"Check: compounding monthly for a year gives {(1 + monthly) ** 12 - 1:.4%}")
```

## Inflation: nominal vs. real

**Inflation** is the rate at which prices rise. If your savings earn 5% while prices rise 3%, your *purchasing power* grows by only about 2%.

- A **nominal** rate is measured in dollars.
- A **real** rate is measured in purchasing power (goods).

The exact relationship is the **Fisher equation**:

\[ (1 + r_{\text{nominal}}) = (1 + r_{\text{real}})(1 + \pi) \quad\Rightarrow\quad r_{\text{real}} = \frac{1 + r_{\text{nominal}}}{1 + \pi} - 1 \approx r_{\text{nominal}} - \pi \]

```python run
for nominal, inflation in [(0.05, 0.03), (0.04, 0.065), (0.12, 0.10), (0.01, 0.0)]:
    real = tv.real_rate(nominal, inflation)
    print(f"nominal {nominal:>5.1%}, inflation {inflation:>5.1%} → real {real:>6.2%}  (approx {nominal - inflation:>6.2%})")
```

### How inflation erodes money

```python run
import matplotlib.pyplot as plt

years = list(range(0, 31))
for pi in [0.02, 0.04, 0.07]:
    plt.plot(years, [100 / (1 + pi) ** t for t in years], label=f"{pi:.0%} inflation")
plt.title("Purchasing power of $100 kept in cash")
plt.xlabel("Years"); plt.ylabel("Value in today's dollars")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

At 4% inflation, cash loses about half its purchasing power in 18 years. That's the Rule of 72 working against you.

> [!NOTE]
> **Be consistent.** Discount nominal cash flows at nominal rates, and real (inflation-adjusted) cash flows at real rates. Mixing them is one of the most common valuation mistakes.

## What determines interest rates?

Any interest rate can be thought of as a sum of building blocks:

\[ r = r^*_{\text{real}} + \text{expected inflation} + \text{default premium} + \text{liquidity premium} + \text{maturity premium} \]

| Component | Compensates for | Example |
|---|---|---|
| Real risk-free rate | Delaying consumption | Short-term inflation-protected Treasury (TIPS) yields |
| Expected inflation | Loss of purchasing power | Why rates rose sharply in 2022 |
| Default premium | Risk the borrower doesn't pay | Junk bonds yield more than Treasuries |
| Liquidity premium | Difficulty selling quickly at a fair price | Small private loans |
| Maturity premium | Price risk of long-term bonds when rates change | 30-year vs. 3-month Treasury |

The **central bank** controls the very shortest risk-free rate (in the US, the federal funds rate). Markets set all the others, building on top of it.

```python run
# Build up a corporate bond yield from components (illustrative numbers)
components = {
    "real risk-free rate": 0.015,
    "expected inflation": 0.025,
    "maturity premium (10y)": 0.008,
    "default premium (BBB)": 0.015,
    "liquidity premium": 0.003,
}
for name, value in components.items():
    print(f"{name:<24} {value:>6.2%}")
print(f"{'required yield':<24} {sum(components.values()):>6.2%}")
```

## Key takeaways

- **EAR** is the true annual rate: \((1 + APR/m)^m - 1\). Compare loans and savings products on EAR.
- Continuous compounding is the limit as compounding gets infinitely frequent: \(e^{rt}\).
- Convert rates between periods with exponents and roots, not by multiplying or dividing.
- **Real rate ≈ nominal rate − inflation**; use the exact Fisher equation for precision.
- Rates are built from a real rate, inflation, and premiums for default, liquidity and maturity.

## Exercises

1. Bank A offers 4.85% compounded monthly. Bank B offers 4.90% compounded annually. Which pays more?
2. A payday lender charges $15 per $100 borrowed for two weeks. What is the APR (26 periods a year)? What is the EAR?
3. Your salary rose from $60,000 to $63,000 while inflation was 6%. What happened to your real income?
4. What nominal return do you need to earn a 4% real return if inflation is 3.5%?

<details>
<summary>Solutions</summary>

```python run
print(f"1. A: {tv.effective_annual_rate(0.0485, 12):.4%}  B: 4.9000%")
period_rate = 15 / 100
print(f"2. APR: {period_rate * 26:.0%}, EAR: {(1 + period_rate) ** 26 - 1:,.0%}")
print(f"3. Real raise: {tv.real_rate(63_000 / 60_000 - 1, 0.06):.2%}  (a real pay cut)")
print(f"4. Required nominal return: {(1.04) * (1.035) - 1:.2%}")
```

</details>

## Watch & read

- [watch] [Khan Academy: Inflation](https://www.khanacademy.org/economics-finance-domain/core-finance/inflation-tutorial). What inflation is, how it is measured, and real vs. nominal returns.
- [watch] [Khan Academy: Interest and debt](https://www.khanacademy.org/economics-finance-domain/core-finance/interest-tutorial). Includes APR vs. EAR and continuous compounding (the number *e*).
- [read] [Investopedia: Effective Annual Interest Rate](https://www.investopedia.com/terms/e/effectiveannualinterestrate.asp). Formula and examples.
- [data] [FRED: Federal Reserve Economic Data](https://fred.stlouisfed.org/). Free data on interest rates and inflation. Search for "DGS10" (10-year Treasury) and "CPIAUCSL" (CPI).
- [read] [U.S. Treasury interest rate data](https://home.treasury.gov/resource-center/data-chart-center/interest-rates). Daily Treasury yields, including real (TIPS) yields.
