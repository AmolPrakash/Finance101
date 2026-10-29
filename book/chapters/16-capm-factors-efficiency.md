# CAPM, Factor Models and Market Efficiency

Chapter 15 showed that only **systematic** risk can't be diversified away. This chapter asks the natural next question: how much extra return should investors expect for bearing it? The **Capital Asset Pricing Model (CAPM)** gives the classic answer. **Factor models** extend it, and the **efficient markets hypothesis** asks whether anyone can consistently beat the market at all.

> [!IMPORTANT]
> **CAPM:** an asset's expected return depends only on its **beta**, its sensitivity to the market portfolio:
> \[ E[R_i] = r_f + \beta_i\,(E[R_m] - r_f) \]
> Firm-specific risk earns no premium, because investors can diversify it away for free.

## From portfolio theory to CAPM

If all investors have the same beliefs and follow Chapter 15's advice, they all hold the same tangency portfolio. In equilibrium, that portfolio must be **the market portfolio**: every asset weighted by its market value. Each asset's risk premium then depends on how much it contributes to the market's risk, which is its beta:

\[ \beta_i = \frac{\text{Cov}(R_i, R_m)}{\text{Var}(R_m)} \]

| Beta | Meaning | Examples |
|---|---|---|
| β = 1 | Moves with the market | Index funds |
| β > 1 | Amplifies market moves | Tech stocks, airlines, small caps |
| 0 < β < 1 | Dampens market moves | Utilities, consumer staples |
| β < 0 | Moves against the market | Rare (some hedges, gold at times) |

## The security market line

```python run
import matplotlib.pyplot as plt
from finance101 import portfolio as pf

rf, rm = 0.04, 0.09
betas = [i / 10 for i in range(0, 26)]
plt.plot(betas, [pf.capm_expected_return(rf, b, rm) * 100 for b in betas], label="Security market line")

stocks = {"Utility": (0.55, 0.075), "Index fund": (1.0, 0.09), "Tech": (1.45, 0.125), "Airline": (1.8, 0.11)}
for name, (b, expected) in stocks.items():
    alpha = expected - pf.capm_expected_return(rf, b, rm)
    plt.scatter([b], [expected * 100], zorder=3)
    plt.annotate(f"{name} (α {alpha:+.1%})", (b, expected * 100), xytext=(5, 5), textcoords="offset points", fontsize=8)
plt.title("CAPM: expected return vs. beta")
plt.xlabel("Beta"); plt.ylabel("Expected return (%)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

An asset plotted **above** the SML offers more return than its risk requires: a positive **alpha** (\(\alpha\)), so it's underpriced. One **below** has a negative alpha. In CAPM equilibrium, all alphas are zero.

## Estimating beta and splitting risk

Regress an asset's excess returns on the market's excess returns:

\[ R_i - r_f = \alpha_i + \beta_i (R_m - r_f) + \varepsilon_i \]

The regression also splits total risk into systematic and idiosyncratic parts:

\[ \sigma_i^2 = \underbrace{\beta_i^2\sigma_m^2}_{\text{systematic}} + \underbrace{\sigma_\varepsilon^2}_{\text{idiosyncratic}} \qquad R^2 = \frac{\beta_i^2\sigma_m^2}{\sigma_i^2} \]

```python run
import numpy as np

rng = np.random.default_rng(42)
n = 120                                                   # 10 years of monthly data (simulated)
market = rng.normal(0.005, 0.045, n)
stock = 0.002 + 1.25 * market + rng.normal(0, 0.06, n)    # true alpha 0.2%/month, beta 1.25

X = np.column_stack([np.ones(n), market])
(alpha, beta), *_ = np.linalg.lstsq(X, stock, rcond=None)
resid = stock - X @ np.array([alpha, beta])

systematic = beta ** 2 * market.var(ddof=1)
total = stock.var(ddof=1)
print(f"Estimated alpha {alpha * 12:.2%} per year, beta {beta:.2f}   (true: 2.4% and 1.25)")
print(f"Total volatility {np.sqrt(total * 12):.1%}: systematic share (R²) {systematic / total:.0%}, idiosyncratic {1 - systematic / total:.0%}")

se_alpha = resid.std(ddof=2) / np.sqrt(n)
print(f"Alpha t-statistic: {alpha / se_alpha:.2f}  (|t| > 2 is the usual bar for 'significant')")
```

Ten years of data gave estimates far from the truth: the true alpha of 2.4% a year is invisible, and even beta is off. Return noise is large relative to alpha. Change the seed and watch the estimates jump around. Keep this in mind in Chapter 18.

## Does CAPM work?

Partly. Higher-beta stocks don't earn as much more than lower-beta stocks as CAPM predicts (the SML is "too flat"), and several characteristics predict returns beyond beta. Still, CAPM remains the most widely used model for the cost of equity because it's simple and captures the central idea: **only undiversifiable risk is rewarded**.

## Factor models

**Multi-factor models** explain returns with several systematic risk factors instead of one. The best known is the **Fama-French three-factor model**:

\[ R_i - r_f = \alpha_i + \beta_{i}(R_m - r_f) + s_i\,SMB + h_i\,HML + \varepsilon_i \]

- **SMB** (small minus big): small-company stocks minus large-company stocks
- **HML** (high minus low): "value" stocks (high book-to-market) minus "growth" stocks

Later models add **momentum**, **profitability** and **investment** factors. A factor regression reveals what really drives a fund's returns:

```python run
rng = np.random.default_rng(7)
n = 240
def factor(mean, vol):
    x = rng.normal(0, vol, n)
    return x - x.mean() + mean            # pin the sample mean so the example is clear

mkt, smb, hml = factor(0.006, 0.045), factor(0.002, 0.03), factor(0.003, 0.03)
# A "skilled stock picker" fund that actually just tilts toward small value stocks:
fund = 0.0 + 1.05 * mkt + 0.6 * smb + 0.5 * hml + rng.normal(0, 0.015, n)

capm_X = np.column_stack([np.ones(n), mkt])
ff_X = np.column_stack([np.ones(n), mkt, smb, hml])
capm_coef, *_ = np.linalg.lstsq(capm_X, fund, rcond=None)
ff_coef, *_ = np.linalg.lstsq(ff_X, fund, rcond=None)

print(f"CAPM alpha:        {capm_coef[0] * 12:+.2%} per year  (looks like skill!)")
print(f"Three-factor alpha:{ff_coef[0] * 12:+.2%} per year")
print(f"Loadings: market {ff_coef[1]:.2f}, SMB {ff_coef[2]:.2f}, HML {ff_coef[3]:.2f}")
```

The fund's apparent "alpha" was really exposure to known factors, something an investor could get cheaply from a small-value index fund.

## The efficient markets hypothesis (EMH)

If prices already reflect available information, you can't consistently earn abnormal returns by trading on it. Eugene Fama distinguished three forms:

| Form | Prices reflect… | Implication |
|---|---|---|
| **Weak** | All past prices and volume | Technical analysis (chart patterns) can't beat the market |
| **Semi-strong** | All public information | Analyzing news and financial statements can't beat the market |
| **Strong** | All information, even private | Even insiders can't beat the market (clearly false; insider trading is illegal for a reason) |

### Testing the weak form: are returns predictable?

If prices follow a **random walk**, today's return tells you nothing about tomorrow's. A simple test is **autocorrelation**:

```python run
def autocorrelation(x, lag=1):
    x = np.asarray(x)
    return np.corrcoef(x[:-lag], x[lag:])[0, 1]

rng = np.random.default_rng(3)
random_walk = rng.normal(0.0004, 0.01, 2_000)
momentum = [0.0]
for shock in rng.normal(0, 0.01, 1_999):
    momentum.append(0.3 * momentum[-1] + shock)          # yesterday predicts today

print(f"Random walk lag-1 autocorrelation: {autocorrelation(random_walk):+.3f}")
print(f"Trending series lag-1 autocorrelation: {autocorrelation(momentum):+.3f}")
```

Real daily stock returns have autocorrelations very close to zero, which is consistent with the weak form.

### Testing the semi-strong form: event studies

An **event study** measures how quickly prices react to news. Compute **abnormal returns** (actual minus expected) around an announcement and add them up into **cumulative abnormal returns (CAR)**:

```python run
rng = np.random.default_rng(11)
days = np.arange(-10, 11)
n_firms = 200
abnormal = rng.normal(0, 0.015, (n_firms, len(days)))
abnormal[:, days == 0] += 0.035                           # good-news surprise on day 0
car = abnormal.mean(axis=0).cumsum()

plt.plot(days, car * 100, marker="o")
plt.axvline(0, color="gray", linestyle="--")
plt.title("Average cumulative abnormal return around good news (simulated)")
plt.xlabel("Days relative to announcement"); plt.ylabel("CAR (%)")
plt.grid(alpha=0.3)
plt.show()
```

In an efficient market, the price jumps **on** the announcement day and then stays flat. A slow drift afterward would mean prices under-react: a profitable anomaly.

### Anomalies and the debate

Researchers have documented patterns that seem to violate efficiency: **momentum**, **value**, **post-earnings-announcement drift**, the **low-volatility** anomaly. Defenders of efficiency argue these are compensation for hidden risks or data mining. Behavioral economists argue they reflect systematic investor errors that persist because arbitrage is costly and risky (Chapter 24). In 2013 the Nobel Prize was shared by **Eugene Fama** (efficiency) and **Robert Shiller** (behavioral finance), along with Lars Peter Hansen.

> [!TIP]
> The practical lesson both camps agree on: beating the market *after costs* is hard, and most active funds fail to do it over long periods. Low-cost diversified index funds are a tough benchmark.

## Key takeaways

- **CAPM:** \(E[R_i] = r_f + \beta_i(E[R_m] - r_f)\); only systematic risk is priced.
- **Alpha** is return beyond what the asset's risk explains; it's hard to measure because returns are noisy.
- **Factor models** (Fama-French and successors) add size, value, momentum and others; much apparent "skill" is factor exposure.
- **EMH:** prices reflect information; weak, semi-strong and strong forms. Anomalies exist, but exploiting them after costs is hard.

## Exercises

1. A stock has beta 1.6. The risk-free rate is 4% and the market's expected return is 10%. What does CAPM predict? If analysts expect 12%, what is the alpha?
2. In the beta regression, change the idiosyncratic noise from 0.06 to 0.02. What happens to R² and the alpha t-statistic?
3. In the factor regression, give the fund a true monthly alpha of 0.3%. Does the three-factor model detect it?

<details>
<summary>Solutions</summary>

```python run
req = pf.capm_expected_return(0.04, 1.6, 0.10)
print(f"1. CAPM: {req:.1%}; alpha {0.12 - req:+.1%}")
rng = np.random.default_rng(42)
m = rng.normal(0.005, 0.045, 120)
s = 0.002 + 1.25 * m + rng.normal(0, 0.02, 120)
(a, b), *_ = np.linalg.lstsq(np.column_stack([np.ones(120), m]), s, rcond=None)
res = s - a - b * m
print(f"2. R² {b ** 2 * m.var(ddof=1) / s.var(ddof=1):.0%}, alpha t-stat {a / (res.std(ddof=2) / np.sqrt(120)):.2f}")
fund_alpha = fund + 0.003
coef, *_ = np.linalg.lstsq(ff_X, fund_alpha, rcond=None)
print(f"3. Three-factor alpha: {coef[0] * 12:+.2%} per year (true 3.6%)")
```

</details>

## Watch & read

- [watch] [Yale ECON 252 (Shiller), lectures "Efficient Markets" and "Behavioral Finance"](https://oyc.yale.edu/economics/econ-252). Both sides of the efficiency debate from a Nobel laureate.
- [read] [The Nobel Prize in Economic Sciences 2013: Fama, Hansen and Shiller](https://www.nobelprize.org/prizes/economic-sciences/2013/summary/). The laureates' lectures on asset pricing and market efficiency.
- [data] [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html). The actual Fama-French factor returns: run real factor regressions on any fund.
- [read] [Investopedia: CAPM](https://www.investopedia.com/terms/c/capm.asp) and [Efficient Market Hypothesis](https://www.investopedia.com/terms/e/efficientmarkethypothesis.asp). Quick references.
