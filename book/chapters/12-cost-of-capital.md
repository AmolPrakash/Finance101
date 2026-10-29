# The Cost of Capital

Every NPV calculation needs a discount rate. Where does it come from? The **cost of capital** is the return a company's investors require for financing it. It's an *opportunity cost*: what those investors could earn elsewhere at the same risk. A project must beat it to create value.

> [!IMPORTANT]
> The cost of capital depends on **the risk of the investment**, not on who is investing or how the money is raised. A risky project needs a high discount rate even inside a safe company.

## The weighted average cost of capital (WACC)

Firms raise money from several sources, each with its own required return. The **WACC** blends them by their **market-value** weights:

\[ WACC = \frac{E}{V} r_E + \frac{D}{V} r_D (1 - t) \qquad V = E + D \]

- \(r_E\): cost of equity, the return shareholders require
- \(r_D\): cost of debt, the return lenders require
- \(t\): the corporate tax rate. Interest is tax-deductible, so debt's after-tax cost is \(r_D(1 - t)\)

We'll estimate each piece for a hypothetical company, **Northwind Logistics**.

## Step 1: Cost of debt

The cost of debt is the **yield to maturity** on the firm's existing long-term bonds, not their coupon rate. The coupon reflects rates when the bonds were issued; the YTM reflects what lenders require today.

```python run
from finance101 import bonds

# Northwind's 12-year bonds: 4.5% semi-annual coupon, trading at $930 per $1,000
r_debt = bonds.yield_to_maturity(930, 1000, 0.045, 12)
tax_rate = 0.25
print(f"Pre-tax cost of debt : {r_debt:.2%}")
print(f"After-tax cost of debt: {r_debt * (1 - tax_rate):.2%}")
```

If the firm has no traded bonds, use the yield on bonds with the same credit rating, or the risk-free rate plus a spread for that rating.

## Step 2: Cost of equity

Shareholders don't state their required return, so we must infer it. The most common tool is the **Capital Asset Pricing Model (CAPM)**, covered fully in Chapter 16:

\[ r_E = r_f + \beta \times (E[R_m] - r_f) \]

- \(r_f\): the risk-free rate (a long-term government bond yield)
- \(E[R_m] - r_f\): the **equity market risk premium**, historically around 4–6% in the US
- \(\beta\): the stock's sensitivity to market movements

### Estimating beta

Beta is the slope of a regression of the stock's returns on the market's returns. Let's estimate it from five years of monthly returns. (The data here is simulated with a known true beta of 1.3, so you can see how well the estimate recovers it.)

```python run
import random
import matplotlib.pyplot as plt
from finance101 import portfolio as pf

rng = random.Random(7)
market = [rng.gauss(0.008, 0.045) for _ in range(60)]
stock = [0.001 + 1.3 * m + rng.gauss(0, 0.04) for m in market]

beta = pf.beta(stock, market)
print(f"Estimated beta: {beta:.2f}  (true value 1.30)")

plt.scatter([m * 100 for m in market], [s * 100 for s in stock], s=14, alpha=0.7)
xs = [min(market), max(market)]
mean_m, mean_s = sum(market) / 60, sum(stock) / 60
plt.plot([x * 100 for x in xs], [(mean_s + beta * (x - mean_m)) * 100 for x in xs], color="black")
plt.title(f"Monthly returns: slope = beta = {beta:.2f}")
plt.xlabel("Market return (%)"); plt.ylabel("Stock return (%)")
plt.grid(alpha=0.3)
plt.show()
```

> [!NOTE]
> Beta estimates are noisy. Re-run the cell with a different seed and watch the estimate move. Practitioners often use **industry betas**, averaging across many similar firms, to reduce the noise. Free industry betas are on Damodaran's site.

```python run
risk_free = 0.043
market_premium = 0.05
r_equity = pf.capm_expected_return(risk_free, beta, risk_free + market_premium)
print(f"Cost of equity (CAPM): {r_equity:.2%}")
```

A sanity check uses the dividend growth model: \(r_E = D_1/P_0 + g\). If the two methods disagree wildly, investigate.

## Step 3: Weights at market value

Use **market** values, not book values: they reflect what investors would pay for each claim today.

```python run
share_price, shares_outstanding = 38.50, 120e6
debt_value = 1_400_000 * 930                    # 1.4 million bonds, each trading at $930

equity_value = share_price * shares_outstanding
total = equity_value + debt_value
print(f"Equity: ${equity_value / 1e9:.2f}bn ({equity_value / total:.1%})")
print(f"Debt  : ${debt_value / 1e9:.2f}bn ({debt_value / total:.1%})")
```

## Step 4: Put it together

```python run
wacc = pf.wacc(equity_value, debt_value, r_equity, r_debt, tax_rate)
print(f"Northwind WACC: {wacc:.2%}")
```

Northwind should accept average-risk projects whose expected returns beat this WACC, and reject those that don't.

## One WACC does not fit all projects

> [!WARNING]
> Using the company-wide WACC for **every** project is a classic mistake. It overvalues risky projects and undervalues safe ones. Over time, the firm drifts toward riskier investments.

Discount each project at a rate that matches **its own** risk. One approach: find **pure-play** companies in the project's line of business and use their beta.

```python run
projects = [  # (name, project beta, expected return)
    ("Warehouse automation", 0.8, 0.088),
    ("Core trucking expansion", 1.1, 0.105),
    ("Drone delivery startup", 2.1, 0.135),
]
print(f"{'Project':<26} {'beta':>5} {'expected':>9} {'required':>9}  WACC rule  Correct rule")
for name, b, expected in projects:
    required = pf.capm_expected_return(risk_free, b, risk_free + market_premium)
    print(f"{name:<26} {b:>5.1f} {expected:>9.1%} {required:>9.1%}  "
          f"{'accept' if expected > wacc else 'reject':<9}  {'accept' if expected > required else 'reject'}")
```

The core expansion has about the same risk as the firm as a whole, so both rules agree. But the firm-wide WACC rejects the safe warehouse project (which beats its own risk-appropriate rate) and accepts the risky drone venture (which doesn't).

```python run
betas = [i / 10 for i in range(0, 26)]
plt.plot(betas, [pf.capm_expected_return(risk_free, b, risk_free + market_premium) * 100 for b in betas], label="Required return (CAPM)")
plt.axhline(wacc * 100, color="gray", linestyle="--", label=f"Company WACC ({wacc:.1%})")
for name, b, expected in projects:
    plt.scatter([b], [expected * 100], zorder=3)
    plt.annotate(name, (b, expected * 100), xytext=(5, 5), textcoords="offset points", fontsize=8)
plt.title("Each project should be judged against its own risk")
plt.xlabel("Project beta"); plt.ylabel("Return (%)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

## Key takeaways

- **WACC** = \(\frac{E}{V} r_E + \frac{D}{V} r_D(1 - t)\), using **market-value** weights.
- **Cost of debt:** the current YTM on the firm's debt, after tax.
- **Cost of equity:** usually CAPM, \(r_f + \beta \times\) market risk premium. Beta estimates are noisy, so industry averages help.
- Use WACC only for projects as risky as the firm overall; otherwise use a **project-specific** rate.

## Exercises

1. Northwind issues more debt so that it's 40% of firm value, and its equity beta rises to 1.55. Recompute WACC (keep the cost of debt the same).
2. A firm has an equity beta of 0.9, a risk-free rate of 4%, a market premium of 5.5%, pre-tax debt cost of 6%, a 21% tax rate and a 30% debt weight. What is its WACC?
3. Change the random seed in the beta cell to 1, 2 and 3. How much does the estimated beta vary?

<details>
<summary>Solutions</summary>

```python run
re_new = pf.capm_expected_return(risk_free, 1.55, risk_free + market_premium)
print(f"1. WACC with 40% debt: {pf.wacc(60, 40, re_new, r_debt, tax_rate):.2%}")
re2 = pf.capm_expected_return(0.04, 0.9, 0.04 + 0.055)
print(f"2. WACC: {pf.wacc(70, 30, re2, 0.06, 0.21):.2%}")
for seed in [1, 2, 3]:
    rng = random.Random(seed)
    m = [rng.gauss(0.008, 0.045) for _ in range(60)]
    s = [0.001 + 1.3 * x + rng.gauss(0, 0.04) for x in m]
    print(f"3. seed {seed}: beta {pf.beta(s, m):.2f}")
```

</details>

## Watch & read

- [watch] [MIT 15.401 Finance Theory I](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/). Later lectures connect CAPM to the cost of capital and capital budgeting.
- [data] [Damodaran Online: cost of capital and betas by industry](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datacurrent.html). Free, updated every January. Industry betas, equity risk premiums and WACCs.
- [read] [Investopedia: Weighted Average Cost of Capital](https://www.investopedia.com/terms/w/wacc.asp). Formula and examples.
- [read] [OpenStax *Principles of Finance*, Chapter 15: How to Think about Investing](https://openstax.org/details/books/principles-finance). Covers CAPM and required returns.
