# Behavioral Finance and Capstone Project

Most of this book assumes people are rational: they weigh risk and return consistently, use all available information and don't make systematic mistakes. Real investors, including professionals, don't always behave that way. **Behavioral finance** studies those predictable departures and asks when they move prices. This chapter introduces the main ideas, then ends with a **capstone project** that pulls together tools from all four courses.

> [!IMPORTANT]
> Behavioral finance doesn't say markets are easy to beat. It says that (1) people make **systematic** errors, and (2) **limits to arbitrage** can stop rational traders from fully correcting the resulting mispricings.

## Prospect theory: how people really value gains and losses

Daniel Kahneman and Amos Tversky found that people judge outcomes as **gains and losses relative to a reference point**, not as final wealth, and that **losses hurt about twice as much as equal gains feel good**. Their value function:

\[ v(x) = \begin{cases} x^{\alpha} & x \ge 0 \\ -\lambda(-x)^{\beta} & x < 0 \end{cases} \qquad \alpha = \beta \approx 0.88,\ \lambda \approx 2.25 \]

```python run
import matplotlib.pyplot as plt

def value(x, alpha=0.88, lam=2.25):
    return x ** alpha if x >= 0 else -lam * (-x) ** alpha

xs = [x for x in range(-100, 101)]
plt.plot(xs, [value(x) for x in xs], label="Prospect theory value")
plt.plot(xs, xs, linestyle="--", color="gray", label="Linear (risk-neutral)")
plt.axhline(0, color="black", linewidth=0.6); plt.axvline(0, color="black", linewidth=0.6)
plt.title("Losses loom larger than gains")
plt.xlabel("Gain or loss ($)"); plt.ylabel("Subjective value")
plt.legend(); plt.grid(alpha=0.3)
plt.show()

coin_flip = 0.5 * value(110) + 0.5 * value(-100)
print(f"Coin flip: win $110 or lose $100. Expected value +$5, but prospect value {coin_flip:.1f} → most people refuse")
```

### Myopic loss aversion

Loss aversion interacts with **how often you look**. Stocks rarely lose money over 20 years but often over a month. An investor who checks daily feels many small losses, finds stocks painful, and demands a big premium to hold them. This is one proposed explanation for the high historical **equity premium**.

```python run
from statistics import NormalDist

mu, sigma = 0.08, 0.17
horizons = {"1 day": 1 / 252, "1 month": 1 / 12, "1 year": 1, "5 years": 5, "20 years": 20}
for label, t in horizons.items():
    p_loss = NormalDist(mu * t, sigma * t ** 0.5).cdf(0)
    print(f"{label:<9} probability of a loss: {p_loss:5.1%}")
```

## A tour of common biases

| Bias | What happens | Typical consequence |
|---|---|---|
| **Overconfidence** | Overestimating your knowledge and skill | Excessive trading; studies find the most active traders earn the least |
| **Disposition effect** | Selling winners too early, holding losers too long | Taxes paid too soon, losses that keep falling |
| **Anchoring** | Fixating on an irrelevant number (e.g. the price you paid) | Slow reaction to new information |
| **Mental accounting** | Treating money differently by label ("house money") | Inconsistent risk-taking |
| **Herding** | Following the crowd | Bubbles and crashes |
| **Recency / extrapolation** | Assuming recent trends will continue | Buying high after booms, selling low after busts |
| **Home bias** | Over-investing in your own country or employer | Under-diversification |

### Overconfidence costs money

```python run
import random
import statistics

def trader_returns(trades_per_year, years=10, cost_per_trade=0.002, seed=0):
    """Traders with zero skill: each trade adds noise and costs."""
    rng = random.Random(seed)
    results = []
    for _ in range(2_000):
        r = 0.0
        for _ in range(years):
            r += 0.07 - trades_per_year * cost_per_trade + rng.gauss(0, 0.16 + 0.004 * trades_per_year)
        results.append(r / years)
    return statistics.mean(results), statistics.stdev(results)

for trades in [1, 10, 25, 50]:
    mean, sd = trader_returns(trades)
    print(f"{trades:>2} trades/year: average annual return {mean:6.2%}, dispersion across traders {sd:5.2%}")
```

## Bubbles and limits to arbitrage

If prices drift away from fundamentals, why don't rational traders correct them immediately? Because arbitrage is **risky and costly**:

- **Noise-trader risk:** the mispricing can get worse before it gets better. "Markets can stay irrational longer than you can stay solvent."
- **Short-selling constraints:** borrowing shares can be expensive or impossible.
- **Capital constraints:** arbitrageurs who lose money face redemptions exactly when the opportunity is best.

A toy model shows how **trend-following** traders can push prices far from fundamental value while **fundamental** traders try to pull them back:

```python run
def simulate_market(trend_weight, days=500, seed=1):
    rng = random.Random(seed)
    fundamental, price, history = 100.0, 100.0, [100.0, 100.0]
    for _ in range(days):
        trend = history[-1] - history[-2]
        value_pull = 0.05 * (fundamental - price)
        price += trend_weight * trend + value_pull + rng.gauss(0, 1.0)
        history.append(price)
    return history

for w in [0.0, 0.6, 0.9]:
    plt.plot(simulate_market(w), linewidth=1, label=f"trend-following strength {w}")
plt.axhline(100, color="black", linestyle="--", linewidth=0.8, label="Fundamental value")
plt.title("Feedback trading creates booms and busts (toy model)")
plt.xlabel("Day"); plt.ylabel("Price")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

> [!TIP]
> Change the `0.05` value-pull strength to `0.01` (weaker arbitrage) and the trend weight to `0.95`. Long, bubble-like swings appear. That's Shiller's "feedback loop" theory of bubbles in miniature.

## Using behavioral insights for good

Behavioral finance also helps people make better decisions:

- **Automatic enrollment** in retirement plans dramatically increases participation (inertia works *for* savers).
- **Save More Tomorrow** programs commit future raises to savings, avoiding the pain of a lower paycheck today.
- Rules like "rebalance once a year" and "own a diversified index fund" protect investors from their own biases.

---

## Capstone project: value a company, build a portfolio, manage its risk

This project uses every course. Work through it in order. Each step has starter code that runs, so modify the assumptions and see how the conclusions change. Treat it as your final exam.

### Part 1 (FIN 101): Read the financials

**Brightline Software** has revenue of $800m, 25% operating margin, $40m depreciation, $60m of capital expenditures and a 21% tax rate. Net working capital is 10% of revenue.

```python run
revenue0, margin, tax = 800.0, 0.25, 0.21
ebit0 = revenue0 * margin
print(f"EBIT {ebit0:.0f}m, NOPAT (after-tax operating profit) {ebit0 * (1 - tax):.0f}m")
```

### Part 2 (FIN 102): Forecast free cash flows and value the firm

Assumptions: revenue growth falls from 12% to 4% over five years, the operating margin rises to 28%, depreciation is 5% and capex 7.5% of revenue, net working capital stays at 10% of revenue, and cash flows grow 3% a year forever after year 5.

```python run
from finance101 import equity, portfolio as pf
from finance101.project_cash_flows import free_cash_flow

growth = [0.12, 0.10, 0.08, 0.06, 0.04]
margins = [0.25, 0.26, 0.27, 0.28, 0.28]
revenues, fcfs = [revenue0], []
for g, m in zip(growth, margins):
    revenues.append(revenues[-1] * (1 + g))
    rev = revenues[-1]
    fcf = free_cash_flow(ebit=rev * m, tax_rate=tax, depreciation=0.05 * rev, capex=0.075 * rev,
                         change_in_nwc=0.10 * (rev - revenues[-2]))
    fcfs.append(fcf)
    print(f"Revenue {rev:7.1f}  FCF {fcf:6.1f}")
```

### Part 3 (FIN 102/201): Estimate the discount rate

```python run
beta_equity, rf, mrp = 1.2, 0.042, 0.05
cost_equity = pf.capm_expected_return(rf, beta_equity, rf + mrp)
debt, cost_debt, shares = 400.0, 0.06, 100.0
market_cap_guess = 4_000.0
wacc = pf.wacc(market_cap_guess, debt, cost_equity, cost_debt, tax)
print(f"Cost of equity {cost_equity:.2%}, WACC {wacc:.2%}")

ev = equity.dcf_value(fcfs, wacc, 0.03)
cash = 150.0
per_share = (ev - debt + cash) / shares
print(f"Enterprise value {ev:,.0f}m → equity value per share ${per_share:.2f}")
```

**Questions:** What share of the value is the terminal value? Build a WACC × terminal growth sensitivity table (Chapter 11). The stock trades at $40 (the price behind `market_cap_guess`). What terminal growth rate, or what margins, is the market pricing in? Is the stock over- or undervalued on your assumptions?

### Part 4 (FIN 201): Build a portfolio around it

You decide to hold Brightline alongside an index fund and bonds. Find a portfolio with a good Sharpe ratio.

```python run
names = ["Brightline", "Index fund", "Bonds"]
mu = [0.11, 0.085, 0.045]
vol = [0.35, 0.16, 0.06]
corr = [[1.0, 0.65, 0.05], [0.65, 1.0, 0.10], [0.05, 0.10, 1.0]]
cov = [[corr[i][j] * vol[i] * vol[j] for j in range(3)] for i in range(3)]

w = pf.tangency_weights(mu, cov, rf)
ret, risk = pf.portfolio_return(w, mu), pf.portfolio_volatility(w, cov)
print("Max-Sharpe weights:", ", ".join(f"{n} {x:.1%}" for n, x in zip(names, w)))
print(f"Expected return {ret:.2%}, volatility {risk:.2%}, Sharpe {(ret - rf) / risk:.2f}")
```

### Part 5 (FIN 202): Measure and hedge the risk

You hold $1 million of this portfolio. Measure its 1-month risk, then buy protective puts on the Brightline position.

```python run
from finance101 import options as opt
from finance101.simulation import monte_carlo_var

var95, es95 = monte_carlo_var(1_000_000, ret, risk, 1 / 12, 0.95, simulations=40_000, seed=7)
print(f"1-month 95% VaR ${var95:,.0f}, expected shortfall ${es95:,.0f}")

brightline_value = 1_000_000 * w[0]
price = 40.0
shares_held = brightline_value / price
put = opt.black_scholes_put(price, 36, 0.25, rf, vol[0])
print(f"Protecting {shares_held:,.0f} shares with 3-month $36 puts costs ${put * shares_held:,.0f} ({put * shares_held / brightline_value:.1%} of the position)")
```

**Extensions:** Price the same put with a binomial tree. Build a collar to reduce the cost. Re-run the VaR with fat-tailed returns. Write a one-page investment memo that defends your valuation and your hedge.

## Where to go next

You've covered the core of four undergraduate finance courses. Natural next steps:

- **Work with real data.** Install Python locally (`pip install pandas yfinance matplotlib`) and redo chapters 14–18 with real prices and the Fama-French factors.
- **Go deeper on valuation.** Work through Damodaran's free valuation course and value a company you know.
- **Go deeper on the math.** Stochastic calculus, time-series econometrics and numerical methods (MIT 18.S096, QuantEcon).
- **Certifications.** The CFA program covers all of this material and much more at a professional level.

## Key takeaways

- **Prospect theory:** people value gains and losses relative to a reference point, and losses hurt about twice as much.
- Biases such as overconfidence, the disposition effect, anchoring and herding are **systematic**, not random.
- **Limits to arbitrage** let mispricings persist; feedback trading can create bubbles.
- The capstone shows how the pieces connect: statements → cash flows → discount rate → value → portfolio → risk → hedge.

## Watch & read

- [watch] [Yale ECON 252 (Shiller), lectures "Behavioral Finance" and "Human Foibles, Fraud, Manipulation, and Regulation"](https://oyc.yale.edu/economics/econ-252). Behavioral finance from one of its founders.
- [read] [The Nobel Prize in Economic Sciences 2002: Daniel Kahneman](https://www.nobelprize.org/prizes/economic-sciences/2002/summary/) and [2017: Richard Thaler](https://www.nobelprize.org/prizes/economic-sciences/2017/summary/). Lectures on prospect theory and behavioral economics.
- [read] [Investopedia: Behavioral Finance](https://www.investopedia.com/terms/b/behavioralfinance.asp). Overview of the main biases.
- [watch] [Aswath Damodaran's valuation lectures](https://www.youtube.com/@AswathDamodaranonValuation). Your next step for the capstone's valuation.
- [read] [Berkshire Hathaway shareholder letters](https://www.berkshirehathaway.com/letters/letters.html). Decades of plain-English lessons on valuation, risk and investor psychology.
