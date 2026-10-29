# Black-Scholes and the Greeks

In 1973, Fischer Black, Myron Scholes and Robert Merton published a formula for the price of a European option. It turned options trading from guesswork into a science, the Chicago Board Options Exchange opened the same year, and Scholes and Merton received the 1997 Nobel Prize (Black had died in 1995). The formula is the continuous-time limit of the binomial tree in Chapter 21, and its sensitivities, the **Greeks**, are how every options desk manages risk today.

> [!IMPORTANT]
> **Black-Scholes call price:**
> \[ C = S\,N(d_1) - K e^{-rT} N(d_2) \]
> \[ d_1 = \frac{\ln(S/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}} \qquad d_2 = d_1 - \sigma\sqrt{T} \]
> where \(N(\cdot)\) is the standard normal cumulative distribution. Only **volatility** \(\sigma\) can't be observed directly.

## The model's assumptions

- The stock follows **geometric Brownian motion**: continuous, log-normally distributed prices with constant volatility.
- The risk-free rate is constant; there are no dividends (the formula extends easily to a dividend yield).
- Trading is continuous and frictionless, and short selling is allowed.
- The option is European.

None of these hold exactly, but the model is a remarkably good first approximation, and practitioners patch its weaknesses with the **volatility smile** (below).

### Reading the formula

- \(N(d_2)\) is the **risk-neutral probability** that the call finishes in the money.
- \(S\,N(d_1)\) is the present value of receiving the stock *if* the option is exercised.
- \(Ke^{-rT}N(d_2)\) is the present value of paying the strike *if* exercised.

```python run
import math
from finance101 import options as opt

S, K, T, r, sigma = 100, 105, 0.5, 0.04, 0.25
d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))
d2 = d1 - sigma * math.sqrt(T)
N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))

print(f"d1 = {d1:.4f}, d2 = {d2:.4f}")
print(f"Risk-neutral P(finish in the money) = N(d2) = {N(d2):.2%}")
print(f"Call = {S} × {N(d1):.4f} − {K}e^(−{r}×{T}) × {N(d2):.4f} = {opt.black_scholes_call(S, K, T, r, sigma):.4f}")
print(f"Put  = {opt.black_scholes_put(S, K, T, r, sigma):.4f}")
```

## How the inputs move the price

```python run
import matplotlib.pyplot as plt

spots = [s / 2 for s in range(120, 281)]
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
for t in [1.0, 0.5, 0.1, 0.001]:
    axes[0].plot(spots, [opt.black_scholes_call(s, 100, t, r, sigma) for s in spots], label=f"T = {t:g}")
axes[0].set_title("Call price vs. stock price"); axes[0].set_xlabel("Stock price"); axes[0].legend()
for v in [0.1, 0.25, 0.5]:
    axes[1].plot(spots, [opt.black_scholes_call(s, 100, 0.5, r, v) for s in spots], label=f"σ = {v:.0%}")
axes[1].set_title("Call price vs. stock price"); axes[1].set_xlabel("Stock price"); axes[1].legend()
for ax in axes:
    ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()
```

| Input rises | Call | Put | Why |
|---|---|---|---|
| Stock price \(S\) | ↑ | ↓ | Closer to (or deeper) in the money |
| Strike \(K\) | ↓ | ↑ | Costs more to buy / pays more to sell |
| Time \(T\) | ↑ | usually ↑ | More time for favorable moves |
| Volatility \(\sigma\) | ↑ | ↑ | More upside; downside is capped |
| Interest rate \(r\) | ↑ | ↓ | The strike is paid later, so its PV is lower |

## Implied volatility and the smile

Every input except volatility is observable. So traders flip the problem around: given the **market price**, solve for the volatility that makes Black-Scholes match it. That's the **implied volatility (IV)**, the market's consensus forecast of future volatility. Options are often quoted in IV rather than dollars.

```python run
market_price = 7.50
iv = opt.implied_volatility(market_price, 100, 100, 0.5, 0.04)   # price, spot, strike, years, rate
print(f"A 6-month at-the-money call trading at ${market_price} implies volatility of {iv:.2%}")
```

If Black-Scholes were exactly right, every option on the same stock would have the same IV. In reality, IV varies with the strike, forming a **smile** or **skew**: out-of-the-money puts are expensive because investors pay up for crash protection. The cell below generates illustrative market prices from a skewed volatility curve, then recovers the implied volatility from each price, just as a trader would from real quotes:

```python run
strikes = list(range(70, 131, 5))
true_skew = {k: 0.22 + 0.25 * (100 - k) / 100 + 0.4 * ((k - 100) / 100) ** 2 for k in strikes}
market_puts = {k: opt.black_scholes_put(100, k, 0.25, 0.04, true_skew[k]) for k in strikes}
recovered = {k: opt.implied_volatility(market_puts[k], 100, k, 0.25, 0.04, kind="put") for k in strikes}

plt.plot(strikes, [recovered[k] * 100 for k in strikes], marker="o")
plt.title("Implied volatility skew (illustrative equity index options)")
plt.xlabel("Strike"); plt.ylabel("Implied volatility (%)")
plt.grid(alpha=0.3)
plt.show()
```

The skew became pronounced after the 1987 crash, when traders realized that large drops are far more likely than a log-normal model allows (Chapter 14's fat tails).

## The Greeks

The Greeks measure how an option's price responds to each input. They're the language of options risk management.

| Greek | Measures sensitivity to | Call | Put |
|---|---|---|---|
| **Delta** \(\Delta\) | Stock price | \(N(d_1)\) | \(N(d_1) - 1\) |
| **Gamma** \(\Gamma\) | Change in delta as the stock moves | \(\frac{N'(d_1)}{S\sigma\sqrt{T}}\) | same |
| **Vega** | Volatility | \(S N'(d_1)\sqrt{T}\) | same |
| **Theta** \(\Theta\) | Passage of time | negative (usually) | usually negative |
| **Rho** \(\rho\) | Interest rate | \(KTe^{-rT}N(d_2)\) | \(-KTe^{-rT}N(-d_2)\) |

```python run
g_call = opt.greeks(100, 105, 0.5, 0.04, 0.25, "call")
g_put = opt.greeks(100, 105, 0.5, 0.04, 0.25, "put")
print(f"{'':<7} {'call':>10} {'put':>10}")
for name in g_call:
    print(f"{name:<7} {g_call[name]:>10.4f} {g_put[name]:>10.4f}")
print(f"\nPractical units: vega per 1 vol point = {g_call['vega'] / 100:.3f}; theta per day = {g_call['theta'] / 365:.4f}")
```

```python run
fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
for t in [0.75, 0.25, 0.05]:
    gs = [opt.greeks(s, 100, t, r, sigma) for s in spots]
    axes[0].plot(spots, [g["delta"] for g in gs], label=f"T = {t}")
    axes[1].plot(spots, [g["gamma"] for g in gs], label=f"T = {t}")
    axes[2].plot(spots, [g["theta"] / 365 for g in gs], label=f"T = {t}")
for ax, title in zip(axes, ["Delta", "Gamma", "Theta per day"]):
    ax.set_title(title); ax.set_xlabel("Stock price"); ax.grid(alpha=0.3)
axes[0].legend()
plt.tight_layout()
plt.show()
```

Near expiry, **gamma** spikes at the money: delta flips from 0 to 1 over a tiny price range, making the option very hard to hedge. Time decay (**theta**) also accelerates for at-the-money options as expiry approaches.

## Delta hedging: how dealers neutralize risk

A dealer who sells a call is exposed if the stock rises. To hedge, the dealer holds \(\Delta\) shares and **rebalances** as delta changes. If Black-Scholes holds, the cost of this dynamic hedge equals the option's price, which is exactly the argument behind the formula.

```python run
import random
import statistics
from finance101.simulation import gbm_path

def hedge_pnl(rebalances, seed, S0=100, K=100, T=0.25, r=0.04, vol=0.25, drift=0.10):
    """Sell one call, delta-hedge it `rebalances` times, return final P&L."""
    rng = random.Random(seed)
    path = gbm_path(S0, drift, vol, T, rebalances, rng)
    dt = T / rebalances
    cash = opt.black_scholes_call(S0, K, T, r, vol)               # premium received
    shares = 0.0
    for i, s in enumerate(path[:-1]):
        target = opt.greeks(s, K, T - i * dt, r, vol)["delta"]
        cash -= (target - shares) * s                              # buy/sell shares to match delta
        shares = target
        cash *= math.exp(r * dt)                                   # cash earns interest
    final = path[-1]
    return cash + shares * final - opt.call_payoff(final, K)

for n in [1, 5, 25, 100]:
    pnls = [hedge_pnl(n, seed) for seed in range(300)]
    print(f"Rebalance {n:>3} times: mean P&L {statistics.mean(pnls):+6.2f}, std dev {statistics.stdev(pnls):5.2f}")
```

With more frequent rebalancing, the hedged P&L clusters ever more tightly around zero, regardless of the stock's real drift (10% here). This is the deep reason option prices don't depend on expected returns.

## Key takeaways

- **Black-Scholes:** \(C = SN(d_1) - Ke^{-rT}N(d_2)\); \(N(d_2)\) is the risk-neutral probability of exercise.
- **Implied volatility** is the volatility that matches the market price; the **smile/skew** shows the model's limits.
- **Greeks:** delta (price), gamma (delta's change), vega (volatility), theta (time), rho (rates).
- **Delta hedging** replicates the option dynamically; its cost equals the Black-Scholes price.

## Exercises

1. Price a 1-year put with S = 50, K = 55, r = 3%, σ = 35%. What are its delta and vega?
2. A 3-month at-the-money call on a $200 stock trades at $12.40 with r = 4%. What is the implied volatility?
3. Estimate the change in the call price from the Greeks cell if the stock rises $2: use \(\Delta \times 2 + \tfrac{1}{2}\Gamma \times 2^2\). Compare with the exact repricing.

<details>
<summary>Solutions</summary>

```python run
p = opt.black_scholes_put(50, 55, 1, 0.03, 0.35)
g = opt.greeks(50, 55, 1, 0.03, 0.35, "put")
print(f"1. Put {p:.4f}, delta {g['delta']:.4f}, vega per vol point {g['vega'] / 100:.4f}")
print(f"2. IV = {opt.implied_volatility(12.40, 200, 200, 0.25, 0.04):.2%}")
approx = g_call["delta"] * 2 + 0.5 * g_call["gamma"] * 4
exact = opt.black_scholes_call(102, 105, 0.5, 0.04, 0.25) - opt.black_scholes_call(100, 105, 0.5, 0.04, 0.25)
print(f"3. Greeks estimate {approx:.4f} vs exact {exact:.4f}")
```

</details>

## Watch & read

- [read] [The Nobel Prize in Economic Sciences 1997: Merton and Scholes](https://www.nobelprize.org/prizes/economic-sciences/1997/summary/). The laureates' lectures and the story of the formula.
- [course] [MIT OCW 18.S096 Topics in Mathematics with Applications in Finance](https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/). Lectures on stochastic calculus, Itô's lemma and the Black-Scholes derivation.
- [read] [Investopedia: Black-Scholes Model](https://www.investopedia.com/terms/b/blackscholes.asp). Formula, assumptions and limitations.
- [course] [Options Industry Council: The Greeks](https://www.optionseducation.org/). Free lessons on delta, gamma, theta and vega in practice.
- [data] [Cboe VIX Index](https://www.cboe.com/tradable_products/vix/). The market's 30-day implied volatility for the S&P 500, the "fear gauge".
