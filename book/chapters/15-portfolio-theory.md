# Portfolio Theory and Diversification

In 1952 Harry Markowitz made a simple observation that won him a Nobel Prize: investors shouldn't judge an asset by its own risk, but by **how it changes the risk of their whole portfolio**. Because assets don't move in lockstep, combining them reduces risk, often without giving up return. Diversification is often called the only free lunch in finance.

> [!IMPORTANT]
> A portfolio's expected return is the weighted average of its assets' returns. Its risk is **less** than the weighted average of their risks whenever correlations are below +1. The lower the correlation, the bigger the risk reduction.

## Two assets

For weights \(w_1, w_2\) (summing to 1), volatilities \(\sigma_1, \sigma_2\) and correlation \(\rho\):

\[ E[R_p] = w_1 E[R_1] + w_2 E[R_2] \]
\[ \sigma_p^2 = w_1^2\sigma_1^2 + w_2^2\sigma_2^2 + 2 w_1 w_2 \rho\, \sigma_1 \sigma_2 \]

The last term is where the magic happens: a low or negative correlation shrinks portfolio variance.

```python run
from finance101 import portfolio as pf

mu_stock, vol_stock = 0.09, 0.18
mu_bond, vol_bond = 0.04, 0.07

for rho in [1.0, 0.5, 0.2, 0.0, -0.5, -1.0]:
    vol = pf.two_asset_volatility(0.6, vol_stock, vol_bond, rho)
    print(f"60/40 portfolio, rho = {rho:+.1f}: return {pf.portfolio_return([0.6, 0.4], [mu_stock, mu_bond]):.1%}, volatility {vol:.2%}")
```

The expected return is the same in every row; only the risk changes.

### The opportunity set

Plotting every possible mix of the two assets traces a curve. The lower the correlation, the more it bends to the left (less risk):

```python run
import matplotlib.pyplot as plt

weights = [i / 100 for i in range(0, 101)]
for rho in [1.0, 0.3, -0.3, -1.0]:
    vols = [pf.two_asset_volatility(w, vol_stock, vol_bond, rho) * 100 for w in weights]
    rets = [(w * mu_stock + (1 - w) * mu_bond) * 100 for w in weights]
    plt.plot(vols, rets, label=f"ρ = {rho:+.1f}")
plt.scatter([vol_stock * 100, vol_bond * 100], [mu_stock * 100, mu_bond * 100], color="black", zorder=3)
plt.annotate("100% stocks", (vol_stock * 100, mu_stock * 100), xytext=(5, -12), textcoords="offset points")
plt.annotate("100% bonds", (vol_bond * 100, mu_bond * 100), xytext=(5, -12), textcoords="offset points")
plt.title("Stock/bond mixes for different correlations")
plt.xlabel("Volatility (%)"); plt.ylabel("Expected return (%)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

### The minimum-variance portfolio

```python run
rho = 0.2
w_min = pf.min_variance_weight(vol_stock, vol_bond, rho)
print(f"Minimum-variance mix: {w_min:.1%} stocks / {1 - w_min:.1%} bonds")
print(f"Its volatility: {pf.two_asset_volatility(w_min, vol_stock, vol_bond, rho):.2%} (lower than 100% bonds at {vol_bond:.0%})")
```

Adding a little of the *riskier* asset lowers risk. That only makes sense once you think about portfolios rather than individual assets.

## Many assets: why diversification works, and where it stops

For an equally weighted portfolio of \(n\) assets with average variance \(\bar{\sigma}^2\) and average covariance \(\overline{\text{cov}}\):

\[ \sigma_p^2 = \frac{1}{n}\bar\sigma^2 + \left(1 - \frac{1}{n}\right)\overline{\text{cov}} \]

As \(n\) grows, the first term (**idiosyncratic** or firm-specific risk) vanishes, but the second (**systematic** or market risk) remains. You can diversify away a company's lawsuit or product failure, but not a recession.

```python run
avg_vol, avg_corr = 0.35, 0.25
avg_var, avg_cov = avg_vol ** 2, avg_corr * avg_vol ** 2

ns = list(range(1, 61))
port_vol = [((avg_var / n) + (1 - 1 / n) * avg_cov) ** 0.5 for n in ns]
plt.plot(ns, [v * 100 for v in port_vol])
plt.axhline(avg_cov ** 0.5 * 100, color="gray", linestyle="--", label="Systematic risk floor")
plt.title("Portfolio volatility vs. number of stocks")
plt.xlabel("Number of stocks (equal weights)"); plt.ylabel("Volatility (%)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()

for n in [1, 5, 10, 20, 50]:
    print(f"{n:>2} stocks: {port_vol[n - 1]:.1%}")
```

Most of the benefit comes from the first 20–30 stocks. Because investors can diversify away firm-specific risk for free, **markets don't reward it**. Only systematic risk earns a premium (Chapter 16).

## The efficient frontier

With more assets, there are many more portfolios. Here are four asset classes with assumed (illustrative) expected returns, volatilities and correlations. We generate thousands of random portfolios and plot them:

```python run
import random

names = ["US stocks", "Intl stocks", "Bonds", "Real estate"]
mu = [0.085, 0.09, 0.04, 0.07]
vol = [0.16, 0.19, 0.06, 0.20]
corr = [[1.0, 0.75, 0.1, 0.6],
        [0.75, 1.0, 0.1, 0.55],
        [0.1, 0.1, 1.0, 0.2],
        [0.6, 0.55, 0.2, 1.0]]
cov = [[corr[i][j] * vol[i] * vol[j] for j in range(4)] for i in range(4)]

rng = random.Random(0)
points = []
for _ in range(4_000):
    raw = [rng.expovariate(1) for _ in range(4)]
    w = [x / sum(raw) for x in raw]                      # random long-only weights
    points.append((pf.portfolio_volatility(w, cov), pf.portfolio_return(w, mu)))

rf = 0.03
plt.scatter([v * 100 for v, _ in points], [r * 100 for _, r in points],
            c=[(r - rf) / v for v, r in points], cmap="viridis", s=6)
plt.colorbar(label="Sharpe ratio")
for i, name in enumerate(names):
    plt.scatter([vol[i] * 100], [mu[i] * 100], color="black", marker="x")
    plt.annotate(name, (vol[i] * 100, mu[i] * 100), xytext=(4, 4), textcoords="offset points", fontsize=8)
plt.title("4,000 random portfolios")
plt.xlabel("Volatility (%)"); plt.ylabel("Expected return (%)")
plt.show()
```

The upper-left edge of the cloud is the **efficient frontier**: the portfolios with the highest return for each level of risk. No rational investor holds a portfolio below it.

## Adding a risk-free asset: the tangency portfolio

Now let investors also lend or borrow at the risk-free rate. Combining the risk-free asset with any risky portfolio gives a straight line, the **capital allocation line (CAL)**. The best line is the steepest one: it touches the frontier at the **tangency portfolio**, the risky portfolio with the **highest Sharpe ratio**.

\[ w_{\text{tangency}} \propto \Sigma^{-1}(\mu - r_f) \]

```python run
w_tan = pf.tangency_weights(mu, cov, rf)
w_mvp = pf.min_variance_weights(cov)
r_tan, v_tan = pf.portfolio_return(w_tan, mu), pf.portfolio_volatility(w_tan, cov)

print("Tangency (max-Sharpe) portfolio:")
for name, w in zip(names, w_tan):
    print(f"  {name:<12} {w:>7.1%}")
print(f"  return {r_tan:.2%}, volatility {v_tan:.2%}, Sharpe {(r_tan - rf) / v_tan:.3f}")
print("\nGlobal minimum-variance portfolio:", ", ".join(f"{n} {w:.0%}" for n, w in zip(names, w_mvp)))
```

> [!NOTE]
> These formulas allow **short selling** (negative weights). With real constraints, such as no shorting or position limits, you need a numerical optimizer, but the idea is the same.

```python run
plt.scatter([v * 100 for v, _ in points], [r * 100 for _, r in points], s=4, color="#bbb")
xs = [0, v_tan * 1.6]
plt.plot([x * 100 for x in xs], [(rf + (r_tan - rf) / v_tan * x) * 100 for x in xs], label="Capital allocation line")
plt.scatter([v_tan * 100], [r_tan * 100], color="red", zorder=3, label="Tangency portfolio")
plt.scatter([0], [rf * 100], color="black", zorder=3, label="Risk-free asset")
plt.title("The best risky portfolio maximizes the Sharpe ratio")
plt.xlabel("Volatility (%)"); plt.ylabel("Expected return (%)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

## Separation: everyone holds the same risky portfolio

The striking result, **two-fund separation**, is that every investor (with the same beliefs) should hold the **same** risky portfolio, the tangency portfolio, and adjust risk only by choosing how much to put in it versus the risk-free asset.

How much? Investors trade off return against risk using a utility like \(U = E[R] - \tfrac{1}{2}A\sigma^2\), where \(A\) measures risk aversion. The optimal share in the risky portfolio is

\[ y^* = \frac{E[R_{tan}] - r_f}{A\,\sigma_{tan}^2} \]

```python run
for A, label in [(2, "aggressive"), (4, "moderate"), (8, "conservative")]:
    y = (r_tan - rf) / (A * v_tan ** 2)
    print(f"Risk aversion {A} ({label:<12}): {y:>6.1%} in the risky portfolio, {1 - y:>6.1%} risk-free")
```

An aggressive investor with \(A = 2\) would put over 100% in the risky portfolio, borrowing at the risk-free rate to invest more.

## Key takeaways

- Portfolio variance depends on **correlations**; combining imperfectly correlated assets reduces risk.
- Diversification eliminates **idiosyncratic** risk but not **systematic** risk.
- The **efficient frontier** contains the best risk-return portfolios; the **tangency portfolio** maximizes the Sharpe ratio.
- With a risk-free asset, everyone holds the same risky portfolio and adjusts risk with leverage or cash.

## Exercises

1. Two assets each have 20% volatility and a correlation of 0.4. What is the volatility of a 50/50 portfolio?
2. Remove "Real estate" from the four-asset example (use only the first three assets). How do the tangency weights and Sharpe ratio change?
3. Using the diversification formula, how many stocks are needed for portfolio volatility to be within 1 percentage point of the systematic floor?

<details>
<summary>Solutions</summary>

```python run
print(f"1. {pf.two_asset_volatility(0.5, 0.2, 0.2, 0.4):.2%}")
mu3, cov3 = mu[:3], [row[:3] for row in cov[:3]]
w3 = pf.tangency_weights(mu3, cov3, rf)
r3, v3 = pf.portfolio_return(w3, mu3), pf.portfolio_volatility(w3, cov3)
print("2.", ", ".join(f"{n} {w:.1%}" for n, w in zip(names, w3)), f"→ Sharpe {(r3 - rf) / v3:.3f}")
floor = avg_cov ** 0.5
n_needed = next(n for n, v in zip(ns, port_vol) if v - floor < 0.01)
print(f"3. {n_needed} stocks")
```

</details>

## Watch & read

- [watch] [Yale ECON 252 (Shiller), lecture "Portfolio Diversification and Supporting Financial Institutions"](https://oyc.yale.edu/economics/econ-252). The Markowitz model and CAPM explained with intuition.
- [watch] [MIT 15.401 Finance Theory I](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/). The "Portfolio Theory" lectures derive the efficient frontier.
- [read] [The Nobel Prize in Economic Sciences 1990: Markowitz, Miller and Sharpe](https://www.nobelprize.org/prizes/economic-sciences/1990/summary/). Background and the laureates' lectures on portfolio theory and asset pricing.
- [read] [Investopedia: Efficient Frontier](https://www.investopedia.com/terms/e/efficientfrontier.asp). A short summary.
- [course] [QuantEcon lectures](https://python.quantecon.org/). Python-based lectures with more advanced optimization techniques.
