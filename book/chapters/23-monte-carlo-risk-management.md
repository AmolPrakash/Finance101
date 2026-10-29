# Monte Carlo Simulation and Risk Management

Some problems have neat formulas; most real ones don't. What's an option worth if its payoff depends on the *average* price over a year? How much could a bank lose on a bad day? When math gets hard, simulate: generate thousands of possible futures, compute the outcome in each, and look at the distribution. This is **Monte Carlo simulation**, named after the casino, and it's the workhorse of modern risk management.

> [!IMPORTANT]
> Monte Carlo replaces an integral with an average. Its error shrinks like \(1/\sqrt{N}\): to make an estimate 10 times more precise, you need 100 times more simulations.

## The idea: estimating π

Throw random darts at a square that contains a quarter circle. The fraction that lands inside the circle approaches \(\pi/4\).

```python run
import random

rng = random.Random(0)
for n in [100, 1_000, 10_000, 100_000]:
    inside = sum(rng.random() ** 2 + rng.random() ** 2 <= 1 for _ in range(n))
    print(f"N = {n:>7,}: π ≈ {4 * inside / n:.4f}")
```

## Simulating stock prices

The standard model for stock prices is **geometric Brownian motion**, the same model behind Black-Scholes:

\[ S_{t+\Delta t} = S_t \exp\!\left[\left(\mu - \tfrac{1}{2}\sigma^2\right)\Delta t + \sigma\sqrt{\Delta t}\,Z\right], \qquad Z \sim N(0, 1) \]

```python run
import matplotlib.pyplot as plt
from finance101.simulation import gbm_path

rng = random.Random(42)
for _ in range(40):
    plt.plot([t / 252 for t in range(253)], gbm_path(100, 0.08, 0.25, 1, 252, rng), linewidth=0.8, alpha=0.7)
plt.title("40 simulated one-year price paths (μ = 8%, σ = 25%)")
plt.xlabel("Years"); plt.ylabel("Price")
plt.grid(alpha=0.3)
plt.show()
```

## Pricing options by simulation

Chapter 21's key insight, **price = discounted risk-neutral expected payoff**, translates directly into code: simulate prices with drift \(r\) (not \(\mu\)), average the payoffs, and discount.

```python run
from finance101 import options as opt
from finance101.simulation import monte_carlo_option

bs = opt.black_scholes_call(100, 100, 1, 0.05, 0.2)
for n in [1_000, 10_000, 50_000]:
    price, se = monte_carlo_option(100, 100, 1, 0.05, 0.2, simulations=n, seed=1)
    print(f"N = {n:>6,}: MC price {price:.4f} ± {1.96 * se:.4f} (95% CI)   Black-Scholes {bs:.4f}")
```

### Faster with NumPy and a variance-reduction trick

Pure Python loops are slow. NumPy runs the same simulation on whole arrays at once. **Antithetic variates** reuse each random draw \(Z\) as \(-Z\) too, which cancels much of the noise for free:

```python run
import numpy as np

def mc_call_numpy(S, K, T, r, vol, n, antithetic=False, seed=0):
    z = np.random.default_rng(seed).standard_normal(n)
    if antithetic:
        z = np.concatenate([z[: n // 2], -z[: n // 2]])
    ST = S * np.exp((r - vol ** 2 / 2) * T + vol * np.sqrt(T) * z)
    disc_payoff = np.exp(-r * T) * np.maximum(ST - K, 0)
    if antithetic:                                   # pair each draw with its mirror image
        disc_payoff = (disc_payoff[: n // 2] + disc_payoff[n // 2:]) / 2
    return disc_payoff.mean(), disc_payoff.std(ddof=1) / np.sqrt(len(disc_payoff))

for anti in [False, True]:
    price, se = mc_call_numpy(100, 100, 1, 0.05, 0.2, 200_000, antithetic=anti)
    print(f"{'Antithetic' if anti else 'Plain':<10} price {price:.4f}, standard error {se:.4f}")
```

### Where Monte Carlo shines: path-dependent options

An **Asian option** pays based on the *average* price over its life. There's no simple closed-form price, but simulation handles it easily:

```python run
def asian_call(S, K, T, r, vol, steps=52, n=40_000, seed=3):
    rng = np.random.default_rng(seed)
    dt = T / steps
    z = rng.standard_normal((n, steps))
    log_paths = np.cumsum((r - vol ** 2 / 2) * dt + vol * np.sqrt(dt) * z, axis=1)
    average = (S * np.exp(log_paths)).mean(axis=1)
    payoff = np.exp(-r * T) * np.maximum(average - K, 0)
    return payoff.mean(), payoff.std(ddof=1) / np.sqrt(n)

price, se = asian_call(100, 100, 1, 0.05, 0.2)
print(f"Asian (average-price) call: {price:.4f} ± {1.96 * se:.4f}")
print(f"Regular European call    : {bs:.4f}  (averaging reduces volatility, so the Asian is cheaper)")
```

## Risk management: Value at Risk

**Value at Risk (VaR)** answers: *what loss will we not exceed with X% confidence over a given horizon?* A 1-day 99% VaR of $2 million means losses should exceed $2 million on only about 1 day in 100.

There are three common ways to compute it:

| Method | How | Strength | Weakness |
|---|---|---|---|
| **Parametric** | Assume normal returns: \(VaR = -(\mu + z_\alpha \sigma)\) | Fast, simple | Misses fat tails |
| **Historical** | Use the actual distribution of past returns | No distribution assumption | Only as good as the history window |
| **Monte Carlo** | Simulate from a model | Handles complex portfolios and options | Model risk, computation |

```python run
from finance101 import risk_return as rr
from finance101.simulation import monte_carlo_var

value = 10_000_000
daily_mu, daily_vol = 0.0003, 0.012

param = rr.parametric_var(daily_mu, daily_vol, 0.99) * value
mc_var, mc_es = monte_carlo_var(value, daily_mu * 252, daily_vol * np.sqrt(252), 1 / 252, 0.99, simulations=50_000, seed=1)

# "Historical" data with fat tails: t-distributed returns with the same volatility
rng = np.random.default_rng(5)
hist = daily_mu + daily_vol * rng.standard_t(4, 1_000) / np.sqrt(2)
hist_var = rr.historical_var(list(hist), 0.99) * value
hist_es = rr.expected_shortfall(list(hist), 0.99) * value

print(f"1-day 99% VaR on a $10m portfolio")
print(f"  Parametric (normal): ${param:>10,.0f}")
print(f"  Monte Carlo (normal): ${mc_var:>10,.0f}   expected shortfall ${mc_es:,.0f}")
print(f"  Historical (fat-tailed data): ${hist_var:>10,.0f}   expected shortfall ${hist_es:,.0f}")
```

### Expected shortfall: what happens beyond VaR?

VaR says nothing about *how bad* the worst days are. **Expected shortfall (ES)**, also called conditional VaR, is the **average loss on days worse than VaR**. Regulators now prefer it (the Basel framework moved bank capital rules from 99% VaR to 97.5% ES).

```python run
losses = -hist * value
var99 = np.quantile(losses, 0.99)
plt.hist(losses / 1e3, bins=80, color="#2f7d6b", alpha=0.85)
plt.axvline(var99 / 1e3, color="black", linestyle="--", label=f"99% VaR ${var99 / 1e3:,.0f}k")
plt.axvline(losses[losses >= var99].mean() / 1e3, color="#b42318", label=f"Expected shortfall ${losses[losses >= var99].mean() / 1e3:,.0f}k")
plt.title("Daily P&L distribution (losses positive)")
plt.xlabel("Loss ($ thousands)"); plt.ylabel("Days")
plt.legend()
plt.show()
```

### Portfolio VaR and diversification

```python run
w = np.array([6_000_000, 4_000_000])          # $ in stocks and bonds
vols = np.array([0.012, 0.004])               # daily volatilities
z99 = 2.326
for corr in [1.0, 0.3, -0.3]:
    cov = np.array([[vols[0] ** 2, corr * vols[0] * vols[1]], [corr * vols[0] * vols[1], vols[1] ** 2]])
    port_var = z99 * np.sqrt(w @ cov @ w)
    standalone = z99 * (w * vols)
    print(f"ρ = {corr:+.1f}: portfolio VaR ${port_var:,.0f}  vs sum of stand-alone VaRs ${standalone.sum():,.0f}")
```

### Backtesting: is the VaR model any good?

Count the days when losses exceeded VaR. At 99%, you expect about 1% exceptions. Here we test a normal-VaR model against fat-tailed "reality":

```python run
from statistics import NormalDist

rng = np.random.default_rng(11)
days = 2_500                                                        # about 10 years
actual = daily_vol * rng.standard_t(3, days) / np.sqrt(3)          # fat tails, same volatility
for confidence in [0.95, 0.99, 0.999]:
    normal_var = -NormalDist(0, daily_vol).inv_cdf(1 - confidence)
    exceptions = int((-actual > normal_var).sum())
    print(f"{confidence:.1%} VaR: expected {days * (1 - confidence):5.1f} exceptions, observed {exceptions:>3}")
```

The normal model looks fine, even conservative, at 95%, but far out in the tail it badly understates risk. Too many exceptions signal that a model underestimates the danger. Under the Basel "traffic light" test, 10 or more exceptions in 250 days puts a bank's model in the red zone.

## Stress testing

VaR describes "normal bad days". **Stress tests** ask what happens in specific extreme scenarios, historical or hypothetical:

```python run
portfolio = {"US stocks": 5_000_000, "Intl stocks": 2_000_000, "Bonds": 2_500_000, "Gold": 500_000}
scenarios = {   # illustrative shocks, not exact historical figures
    "2008-style crisis": {"US stocks": -0.45, "Intl stocks": -0.50, "Bonds": 0.05, "Gold": 0.05},
    "2022-style inflation shock": {"US stocks": -0.20, "Intl stocks": -0.18, "Bonds": -0.15, "Gold": 0.0},
    "Rate cut rally": {"US stocks": 0.12, "Intl stocks": 0.10, "Bonds": 0.06, "Gold": 0.08},
}
for name, shocks in scenarios.items():
    pnl = sum(portfolio[a] * shocks[a] for a in portfolio)
    print(f"{name:<28} P&L ${pnl:>12,.0f}  ({pnl / sum(portfolio.values()):+.1%})")
```

The 2022-style scenario matters: the usual stock-bond diversification **failed** when both fell together. Stress tests catch correlation breakdowns that VaR models calibrated on calm periods miss.

## Key takeaways

- **Monte Carlo** estimates values as averages over simulated scenarios; error ∝ \(1/\sqrt{N}\).
- Price derivatives by simulating **risk-neutral** paths; it's ideal for path-dependent payoffs.
- **VaR** gives a loss threshold; **expected shortfall** measures the tail beyond it.
- Normal-based VaR **understates** fat-tailed risk; backtest models and complement them with **stress tests**.

## Exercises

1. Price a 6-month put with S = 50, K = 48, r = 4%, σ = 30% by Monte Carlo (use `monte_carlo_option` with `kind="put"`). Compare with Black-Scholes.
2. Compute the 10-day 99% parametric VaR for the $10m portfolio using the square-root-of-time rule.
3. Add a "Tech crash" scenario (US stocks −30%, Intl −15%, Bonds +3%, Gold +2%) to the stress test.

<details>
<summary>Solutions</summary>

```python run
p, se = monte_carlo_option(50, 48, 0.5, 0.04, 0.3, simulations=50_000, kind="put", seed=2)
print(f"1. MC put {p:.4f} ± {1.96 * se:.4f}; Black-Scholes {opt.black_scholes_put(50, 48, 0.5, 0.04, 0.3):.4f}")
print(f"2. 10-day VaR ≈ ${rr.parametric_var(0, daily_vol, 0.99) * np.sqrt(10) * value:,.0f}")
shock = {"US stocks": -0.30, "Intl stocks": -0.15, "Bonds": 0.03, "Gold": 0.02}
print(f"3. Tech crash P&L: ${sum(portfolio[a] * shock[a] for a in portfolio):,.0f}")
```

</details>

## Watch & read

- [course] [MIT OCW 18.S096 Topics in Mathematics with Applications in Finance](https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/). Lectures on Monte Carlo methods and risk modeling.
- [course] [QuantEcon lectures](https://python.quantecon.org/). Python-based lectures on simulation and stochastic processes.
- [read] [Investopedia: Value at Risk](https://www.investopedia.com/terms/v/var.asp) and [Monte Carlo Simulation](https://www.investopedia.com/terms/m/montecarlosimulation.asp). Short references.
- [read] [Federal Reserve: Stress tests](https://www.federalreserve.gov/supervisionreg/stress-tests-capital-planning.htm). How regulators stress-test the largest US banks, with published scenarios.
- [read] [OpenStax *Principles of Finance*, Chapter 20: Risk Management and the Financial Manager](https://openstax.org/details/books/principles-finance). Corporate risk management and hedging.
