# Performance Evaluation

A fund returned 14% last year while the market returned 10%. Is the manager skilled? Maybe. Or maybe the fund took more risk, got lucky, or tilted toward a factor that happened to do well. **Performance evaluation** separates skill from risk and luck. It matters enormously: investors pay billions in fees for active management every year.

> [!IMPORTANT]
> Raw returns aren't enough. Judge performance **relative to the risk taken** and **relative to an appropriate benchmark**, and remember that even large differences in returns can be pure luck.

## The risk-adjusted performance measures

| Measure | Formula | Use when… |
|---|---|---|
| **Sharpe ratio** | \(\frac{\bar R_p - r_f}{\sigma_p}\) | The fund is your whole portfolio (total risk matters) |
| **Sortino ratio** | \(\frac{\bar R_p - r_f}{\sigma_{\text{downside}}}\) | You care mostly about losses |
| **Treynor ratio** | \(\frac{\bar R_p - r_f}{\beta_p}\) | The fund is one piece of a diversified portfolio (only systematic risk matters) |
| **Jensen's alpha** | \(\bar R_p - [r_f + \beta_p(\bar R_m - r_f)]\) | You want the return beyond what CAPM predicts |
| **Information ratio** | \(\frac{\bar R_p - \bar R_b}{\text{tracking error}}\) | Judging an active manager against a benchmark |
| **M²** | Sharpe ratio scaled to the market's volatility | Comparing Sharpe ratios in "return" units |

Let's evaluate three simulated funds over 10 years of monthly data:

- **Leveraged Index:** just the market with 1.5x leverage, so it has no skill.
- **Steady Picker:** a low-beta fund with genuine stock-picking skill.
- **Closet Indexer:** charges active fees but mostly hugs the index.

```python run
import random
import statistics
from finance101 import performance as perf, risk_return as rr

rng = random.Random(10)
months = 120
rf = 0.03 / 12

def noise(sd):
    """Random monthly shocks, re-centered on zero so the example's averages come out as designed."""
    x = [rng.gauss(0, sd) for _ in range(months)]
    avg = statistics.mean(x)
    return [v - avg for v in x]

market = [0.008 + e for e in noise(0.045)]                     # about 9.6% a year
funds = {
    "Leveraged Index": [rf + 1.5 * (m - rf) + e for m, e in zip(market, noise(0.005))],
    "Steady Picker": [rf + 0.7 * (m - rf) + 0.003 + e for m, e in zip(market, noise(0.015))],
    "Closet Indexer": [m - 0.001 + e for m, e in zip(market, noise(0.004))],
    "Market": market,
}

print(f"{'Fund':<16} {'Return':>7} {'Vol':>6} {'Beta':>5} {'Sharpe':>7} {'Sortino':>8} {'Treynor':>8} {'Alpha':>7} {'IR':>6}")
for name, r in funds.items():
    ann_ret = statistics.mean(r) * 12
    b = statistics.covariance(r, market) / statistics.variance(market)
    ir = perf.information_ratio(r, market, 12) if name != "Market" else float("nan")
    print(f"{name:<16} {ann_ret:>7.1%} {rr.volatility(r, 12):>6.1%} {b:>5.2f} "
          f"{rr.sharpe_ratio(r, 0.03, 12):>7.2f} {perf.sortino_ratio(r, rf, 12):>8.2f} "
          f"{perf.treynor_ratio(r, b, rf, 12):>8.1%} {perf.jensens_alpha(r, market, rf, 12):>7.1%} {ir:>6.2f}")
```

Read the table carefully:

- The **Leveraged Index** has the highest raw return, but its alpha is about zero and its Sharpe ratio matches the market's. It's just more risk. Its information ratio looks respectable only because the market is the wrong benchmark for a fund with a beta of 1.5.
- The **Steady Picker** earns less than the Leveraged Index with half the volatility. It has a clearly positive alpha and the best Sharpe and Treynor ratios. It's the only one adding value.
- The **Closet Indexer** delivers the market minus fees: negative alpha.

### M²: Sharpe ratio in return units

M² (Modigliani-squared) asks: what return would the fund have earned if it were levered up or down to the **market's volatility**?

\[ M^2 = r_f + \text{Sharpe}_p \times \sigma_m \]

```python run
vol_m = rr.volatility(market, 12)
for name, r in funds.items():
    m2 = 0.03 + rr.sharpe_ratio(r, 0.03, 12) * vol_m
    print(f"{name:<16} M² = {m2:.2%}")
```

## Skill or luck?

Returns are noisy. How long must we watch a manager to be confident that a positive alpha is real? The alpha's t-statistic is roughly

\[ t \approx \frac{\alpha}{\text{tracking error}} \sqrt{T} = IR \times \sqrt{T} \]

To reach \(t = 2\), you need about \(T = (2 / IR)^2\) years:

For an information ratio of 0.5, which is excellent, that's 16 years. For 0.25, which is good, it's 64 years.

```python run
for ir in [1.0, 0.5, 0.3, 0.2]:
    print(f"Information ratio {ir:.1f}: about {(2 / ir) ** 2:>4.0f} years to be statistically confident")
```

### A tournament of monkeys

Simulate 1,000 managers with **zero** skill. After 5 years, some will look brilliant purely by chance. Do they keep winning?

```python run
import matplotlib.pyplot as plt

rng = random.Random(5)
n_managers, te = 1_000, 0.05 / 12 ** 0.5           # 5% annual tracking error, zero true alpha

def active_return(years):
    return [statistics.mean(rng.gauss(0, te) for _ in range(12 * years)) * 12 for _ in range(n_managers)]

first, second = active_return(5), active_return(5)
ranked = sorted(range(n_managers), key=lambda i: first[i], reverse=True)
top = ranked[:100]

print(f"Top 100 managers' average active return, years 1-5 : {statistics.mean(first[i] for i in top):+.2%} per year")
print(f"The same managers, years 6-10                      : {statistics.mean(second[i] for i in top):+.2%} per year")
print(f"Best manager in years 1-5: {first[ranked[0]]:+.2%}/yr → years 6-10: {second[ranked[0]]:+.2%}/yr")

plt.scatter([f * 100 for f in first], [s * 100 for s in second], s=6, alpha=0.5)
plt.title("No skill: past performance doesn't predict future performance")
plt.xlabel("Active return, years 1-5 (%/yr)"); plt.ylabel("Active return, years 6-10 (%/yr)")
plt.grid(alpha=0.3)
plt.show()
```

> [!WARNING]
> **Survivorship bias** makes things worse. Funds that perform badly are closed or merged away, so databases of "existing funds" look better than the funds investors actually experienced. Always ask what happened to the losers.

## Performance attribution

When a fund does beat its benchmark, **attribution** explains *why*. The **Brinson model** splits active return into:

- **Allocation:** overweighting sectors that outperformed
- **Selection:** picking better stocks within each sector

```python run
#            benchmark weight, fund weight, benchmark return, fund return
sectors = {
    "Technology": (0.30, 0.40, 0.18, 0.20),
    "Healthcare": (0.20, 0.15, 0.06, 0.09),
    "Financials": (0.25, 0.20, 0.10, 0.08),
    "Energy":     (0.25, 0.25, -0.02, 0.01),
}
bench_total = sum(wb * rb for wb, _, rb, _ in sectors.values())
fund_total = sum(wf * rf_ for _, wf, _, rf_ in sectors.values())

print(f"{'Sector':<11} {'Allocation':>11} {'Selection':>10}")
alloc_sum = select_sum = 0
for name, (wb, wf, rb, rf_) in sectors.items():
    allocation = (wf - wb) * (rb - bench_total)
    selection = wf * (rf_ - rb)
    alloc_sum += allocation
    select_sum += selection
    print(f"{name:<11} {allocation:>+11.2%} {selection:>+10.2%}")
print(f"{'Total':<11} {alloc_sum:>+11.2%} {select_sum:>+10.2%}")
print(f"\nFund {fund_total:.2%} − benchmark {bench_total:.2%} = {fund_total - bench_total:+.2%} = allocation + selection")
```

## Key takeaways

- Use **Sharpe/Sortino** for total portfolios, **Treynor/alpha** for pieces of diversified portfolios, and the **information ratio** for benchmark-relative management.
- High raw returns often just reflect high risk (leverage or beta).
- Distinguishing skill from luck takes **many years** of data; past winners often revert to average.
- **Attribution** splits active return into allocation and selection effects.

## Exercises

1. A fund has an annual excess return of 3% and tracking error of 4%. What is its information ratio, and how many years of data would you need to reach t = 2?
2. Raise the Steady Picker's monthly alpha from 0.3% to 0.6% and re-run the first table. How do its rankings change?
3. In the manager tournament, give every manager a true alpha of +1% a year. Does the scatter plot change?

<details>
<summary>Solutions</summary>

```python run
ir = 0.03 / 0.04
print(f"1. IR = {ir:.2f}; years for t = 2: {(2 / ir) ** 2:.1f}")
skilled = [rf + 0.7 * (m - rf) + 0.006 + e for m, e in zip(market, noise(0.015))]
print(f"2. Alpha {perf.jensens_alpha(skilled, market, rf, 12):.1%}, Sharpe {rr.sharpe_ratio(skilled, 0.03, 12):.2f}")
print("3. The whole cloud shifts up and right by about 1%, but the correlation between periods stays near zero.")
```

</details>

## Watch & read

- [watch] [Yale ECON 252 (Shiller), lecture "Professional Money Managers and Their Influence"](https://oyc.yale.edu/economics/econ-252). How the fund industry works and how managers are judged.
- [read] [Investopedia: Jensen's Measure](https://www.investopedia.com/terms/j/jensensmeasure.asp) and [Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp). Quick references.
- [read] [S&P Dow Jones Indices: SPIVA scorecards](https://www.spglobal.com/spdji/en/research-insights/spiva/). Free twice-yearly reports on how many active funds beat their benchmarks (most don't).
- [data] [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html). Factor returns to compute real alphas for any fund.
