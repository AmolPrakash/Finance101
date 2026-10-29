# Measuring Risk and Return

FIN 102 used discount rates that "reflect risk" without saying exactly what risk is or how to measure it. FIN 201 fills that gap. This chapter builds the statistical toolkit, covering returns, averages, volatility, distributions and drawdowns, that the rest of investments rests on.

> [!IMPORTANT]
> Investors care about the **whole distribution** of possible outcomes, not just the average. The main summary statistics are the **expected return** (the center) and the **volatility** (the spread). Higher expected returns come only with higher risk.

## Measuring returns

The **holding-period return** combines income and price change:

\[ R_t = \frac{P_t + D_t - P_{t-1}}{P_{t-1}} \]

```python run
from finance101 import risk_return as rr

prices = [100, 108, 97, 104, 115, 109, 121]
returns = rr.simple_returns(prices)
print("Returns:", [f"{r:+.1%}" for r in returns])
print(f"Cumulative return: {rr.cumulative_return(returns):.2%}")
```

### Arithmetic vs. geometric average

Suppose a stock rises 50% then falls 50%. The **arithmetic** average return is 0%, but you've lost money: $100 → $150 → $75. The **geometric** average, the constant rate that gives the same ending wealth, is the honest measure of compound growth:

\[ \bar{R}_{\text{geo}} = \left[\prod_{t=1}^{T}(1 + R_t)\right]^{1/T} - 1 \]

```python run
import statistics

swings = [0.50, -0.50]
arith = statistics.mean(swings)
geo = rr.annualized_return(swings, periods_per_year=1)
print(f"Arithmetic mean: {arith:.1%}   Geometric mean: {geo:.1%}")

print(f"\nFor the price series above: arithmetic {statistics.mean(returns):.2%}, geometric {rr.annualized_return(returns, 1):.2%}")
```

The gap between them is called **volatility drag**: approximately \(\bar R_{geo} \approx \bar R_{arith} - \tfrac{1}{2}\sigma^2\). More volatile investments compound more slowly than their average return suggests.

> [!NOTE]
> Use the **arithmetic** mean to estimate *next year's* expected return; use the **geometric** mean to describe *past* compound growth.

### Log returns

**Log returns**, \(\ln(P_t / P_{t-1})\), add up over time, which makes multi-period math easy. They're standard in derivatives and risk models.

```python run
logs = rr.log_returns(prices)
print(f"Sum of log returns: {sum(logs):.4f}  =  ln(P_end / P_start) = {__import__('math').log(prices[-1] / prices[0]):.4f}")
```

## Expected return and variance from scenarios

When you think in terms of scenarios with probabilities:

\[ E[R] = \sum_s p_s R_s \qquad \sigma^2 = \sum_s p_s (R_s - E[R])^2 \]

```python run
scenarios = {"recession": (0.20, -0.18), "normal": (0.55, 0.09), "boom": (0.25, 0.28)}
expected = sum(p * r for p, r in scenarios.values())
variance = sum(p * (r - expected) ** 2 for p, r in scenarios.values())
print(f"Expected return: {expected:.2%}   Volatility: {variance ** 0.5:.2%}")
```

## Volatility from historical data

With historical data, estimate volatility as the sample standard deviation. To **annualize** it, multiply by the square root of the number of periods per year. Variance grows linearly with time, so standard deviation grows with its square root:

\[ \sigma_{\text{annual}} = \sigma_{\text{daily}} \times \sqrt{252} \qquad \sigma_{\text{annual}} = \sigma_{\text{monthly}} \times \sqrt{12} \]

The cells below use simulated monthly returns calibrated to long-run US averages (roughly 10% a year with 16% volatility for stocks, 5% and 6% for bonds, 3% and 1% for T-bills). The data is simulated, not historical, so you can change the parameters and see what happens.

```python run
import random

rng = random.Random(2024)
months = 12 * 30
assets = {"Stocks": (0.10, 0.16), "Bonds": (0.05, 0.06), "T-bills": (0.03, 0.01)}
monthly = {name: [rng.gauss(mu / 12, sigma / 12 ** 0.5) for _ in range(months)] for name, (mu, sigma) in assets.items()}

print(f"{'':<8} {'mean (ann.)':>12} {'vol (ann.)':>11} {'CAGR':>8} {'worst month':>12}")
for name, rets in monthly.items():
    print(f"{name:<8} {statistics.mean(rets) * 12:>12.2%} {rr.volatility(rets, 12):>11.2%} "
          f"{rr.annualized_return(rets, 12):>8.2%} {min(rets):>12.2%}")
```

```python run
import matplotlib.pyplot as plt

for name, rets in monthly.items():
    wealth, path = 1.0, [1.0]
    for r in rets:
        wealth *= 1 + r
        path.append(wealth)
    plt.plot([m / 12 for m in range(months + 1)], path, label=name)
plt.yscale("log")
plt.title("Growth of $1 (simulated, log scale)")
plt.xlabel("Years"); plt.ylabel("Wealth ($, log scale)")
plt.legend(); plt.grid(alpha=0.3, which="both")
plt.show()
```

A log scale makes constant growth rates look like straight lines, so you can compare growth across very different magnitudes.

## Risk-adjusted return: the Sharpe ratio

To compare investments with different risks, measure the **excess return over the risk-free rate per unit of volatility**:

\[ \text{Sharpe ratio} = \frac{E[R] - r_f}{\sigma} \]

```python run
rf_annual = 0.03
for name in ["Stocks", "Bonds"]:
    print(f"{name:<7} Sharpe ratio: {rr.sharpe_ratio(monthly[name], rf_annual, 12):.2f}")
```

## Are returns normally distributed?

Many models assume returns follow a normal ("bell curve") distribution. Real returns have **fat tails**: extreme days happen far more often than a normal distribution predicts. On October 19, 1987, US stocks fell over 20% in a single day, an event a normal model says should essentially never happen.

Let's compare normal returns with a fat-tailed (Student-t) distribution that has the same volatility:

```python run
import math

def student_t(rng, df):
    chi2 = sum(rng.gauss(0, 1) ** 2 for _ in range(df))
    return rng.gauss(0, 1) / math.sqrt(chi2 / df)

rng = random.Random(1)
n, daily_vol, df = 20_000, 0.01, 4
normal = [rng.gauss(0, daily_vol) for _ in range(n)]
scale = daily_vol / math.sqrt(df / (df - 2))           # match the variance
fat = [scale * student_t(rng, df) for _ in range(n)]

def excess_kurtosis(x):
    m, s = statistics.mean(x), statistics.pstdev(x)
    return sum(((v - m) / s) ** 4 for v in x) / len(x) - 3

for name, data in [("Normal", normal), ("Fat-tailed", fat)]:
    big = sum(abs(v) > 4 * daily_vol for v in data)
    print(f"{name:<11} vol {statistics.pstdev(data):.4f}  excess kurtosis {excess_kurtosis(data):5.2f}  days beyond 4σ: {big}")

bins = [i / 1000 for i in range(-60, 61, 2)]
plt.hist(normal, bins=bins, alpha=0.6, label="Normal", density=True)
plt.hist(fat, bins=bins, alpha=0.6, label="Fat-tailed (t, 4 df)", density=True)
plt.yscale("log")
plt.title("Same volatility, very different tails")
plt.xlabel("Daily return"); plt.ylabel("Density (log scale)")
plt.legend()
plt.show()
```

> [!WARNING]
> Risk models that assume normality **understate** the chance of a crash. That was one lesson of 2008. Chapter 23 shows tail risk measures that don't depend on normality.

## Drawdowns

Volatility treats up and down moves alike, but investors feel losses from a **peak** much more. The **maximum drawdown** is the largest peak-to-trough decline:

```python run
wealth, path = 100.0, [100.0]
for r in monthly["Stocks"]:
    wealth *= 1 + r
    path.append(wealth)

peaks, peak = [], path[0]
for p in path:
    peak = max(peak, p)
    peaks.append(peak)
drawdowns = [p / pk - 1 for p, pk in zip(path, peaks)]

print(f"Maximum drawdown: {rr.max_drawdown(path):.1%}")
plt.fill_between(range(len(drawdowns)), [d * 100 for d in drawdowns], 0, alpha=0.5, color="#b42318")
plt.title("Drawdown from previous peak (simulated stocks)")
plt.xlabel("Month"); plt.ylabel("Drawdown (%)")
plt.show()
```

## Key takeaways

- Use **geometric** averages for past compound growth and **arithmetic** averages for expected returns; volatility creates the gap.
- **Volatility** (standard deviation) is the standard risk measure; annualize it with \(\sqrt{T}\).
- The **Sharpe ratio** measures excess return per unit of risk.
- Real returns have **fat tails**; drawdowns capture the losses investors actually experience.

## Exercises

1. A fund returned +25%, −10%, +15%, −20%, +30% over five years. Compute its arithmetic mean, geometric mean and volatility.
2. Daily volatility is 1.2%. What is the annualized volatility? The monthly volatility?
3. Change the simulated stock volatility to 25% and re-run the simulation cells. What happens to the CAGR and maximum drawdown?

<details>
<summary>Solutions</summary>

```python run
fund = [0.25, -0.10, 0.15, -0.20, 0.30]
print(f"1. arithmetic {statistics.mean(fund):.2%}, geometric {rr.annualized_return(fund, 1):.2%}, volatility {rr.volatility(fund):.2%}")
print(f"2. annual {0.012 * 252 ** 0.5:.2%}, monthly {0.012 * 21 ** 0.5:.2%}")
print("3. Higher volatility lowers the CAGR (volatility drag) and deepens drawdowns.")
```

</details>

## Watch & read

- [watch] [MIT 15.401 Finance Theory I](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/). The "Risk and Return" lectures cover these statistics with historical data.
- [course] [MIT OCW 18.S096 Topics in Mathematics with Applications in Finance](https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/). Free video lectures on probability, time series and volatility modeling, for when you want the math.
- [read] [OpenStax *Principles of Finance*, Chapters 12–13](https://openstax.org/details/books/principles-finance). Historical performance of US markets and statistical analysis in finance.
- [read] [Investopedia: Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp). Definition and caveats.
- [data] [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html). Free historical US market and factor returns back to 1926. Download a CSV and analyze it with these tools.
