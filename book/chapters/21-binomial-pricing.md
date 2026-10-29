# Binomial Option Pricing

How much should a call option cost? You might guess "the expected payoff, discounted." But expected under which probabilities, and discounted at what rate? The option is riskier than the stock, and it's not clear how to adjust. The binomial model sidesteps both questions with one of the most beautiful ideas in finance: **replication**.

> [!IMPORTANT]
> If you can build a portfolio of stock and bonds that pays exactly the same as the option in every scenario, the option must cost the same as that portfolio. No assumptions about risk preferences or expected returns are needed.

## One step: replicating a call

A stock is at $100. In one year it will be either **$120** or **$80**. The risk-free rate is 0% (to keep things simple). What is a call with strike $100 worth?

```
            S = 120   → call pays 20
  S = 100 <
            S = 80    → call pays 0
```

Build a portfolio of \(\Delta\) shares and \(B\) dollars of bonds that matches the call in both states:

\[ 120\Delta + B = 20 \qquad 80\Delta + B = 0 \]

Subtracting: \(40\Delta = 20\), so \(\Delta = 0.5\) and \(B = -40\) (borrow $40).

```python run
from finance101 import binomial as bn

delta, bond, value = bn.one_step_replication(spot=100, up_price=120, down_price=80, strike=100, rate=0.0, years=1)
print(f"Buy {delta} shares, bond position {bond:+.2f} → costs {value:.2f} today")
for s in [120, 80]:
    print(f"  If S = {s}: portfolio worth {delta * s + bond:.2f}, call pays {max(s - 100, 0)}")
```

The call must cost **$10**. If it traded at $12, you'd sell the call, buy the replicating portfolio for $10, and pocket $2 risk-free.

Notice what we **didn't** need: the probability that the stock goes up. Whether it's 90% or 10%, the option is worth $10, because the stock price already reflects those probabilities.

## Risk-neutral pricing

There's a shortcut. Define the **risk-neutral probability** \(p\) as the up-probability that makes the stock earn exactly the risk-free rate:

\[ p = \frac{e^{r\Delta t} - d}{u - d} \]

where \(u\) and \(d\) are the up and down factors. Then *any* derivative's price is its expected payoff under \(p\), discounted at the risk-free rate:

\[ V = e^{-r\Delta t}\,[\,p\,V_u + (1 - p)\,V_d\,] \]

```python run
import math

u, d_, r, dt = 1.2, 0.8, 0.0, 1.0
p = (math.exp(r * dt) - d_) / (u - d_)
print(f"Risk-neutral up probability: {p:.2f}")
print(f"Call value = {math.exp(-r * dt) * (p * 20 + (1 - p) * 0):.2f}  (same as replication)")
```

\(p\) isn't anyone's real belief. It's a pricing device that bakes the market's risk adjustment into the probabilities. That's why the same trick, **price = discounted risk-neutral expectation**, underlies nearly all of derivatives pricing, including Black-Scholes and Monte Carlo.

## Multi-step trees

One step with two outcomes is crude. Split the time to expiry into many small steps and the tree can approximate realistic price distributions. The **Cox-Ross-Rubinstein (CRR)** tree sets

\[ u = e^{\sigma\sqrt{\Delta t}} \qquad d = 1/u \]

so that the tree matches the stock's volatility \(\sigma\). Work **backwards** from expiry: at each node, the option value is the discounted risk-neutral average of the two nodes after it.

```python run
def show_tree(spot, strike, years, rate, vol, steps, kind="call", american=False):
    dt = years / steps
    up, down, p = bn.crr_parameters(vol, rate, dt)
    disc = math.exp(-rate * dt)
    exercise = (lambda s: max(s - strike, 0)) if kind == "call" else (lambda s: max(strike - s, 0))
    stock = [[spot * up ** j * down ** (i - j) for j in range(i + 1)] for i in range(steps + 1)]
    value = [[0.0] * (i + 1) for i in range(steps + 1)]
    value[steps] = [exercise(s) for s in stock[steps]]
    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            cont = disc * (p * value[i + 1][j + 1] + (1 - p) * value[i + 1][j])
            value[i][j] = max(cont, exercise(stock[i][j])) if american else cont
    print(f"u = {up:.4f}, d = {down:.4f}, risk-neutral p = {p:.4f}")
    for i in range(steps + 1):
        cells = "  ".join(f"{stock[i][j]:6.1f}|{value[i][j]:5.2f}" for j in range(i, -1, -1))
        print(f"step {i}: {cells}")
    return value[0][0]

price = show_tree(spot=100, strike=100, years=1, rate=0.05, vol=0.2, steps=3)
print(f"\n3-step call price: {price:.4f}   (each cell shows stock|option)")
```

## Convergence to Black-Scholes

As the number of steps grows, the binomial price converges to the Black-Scholes price (Chapter 22):

```python run
import matplotlib.pyplot as plt
from finance101 import options as opt

bs = opt.black_scholes_call(100, 100, 1, 0.05, 0.2)
steps = list(range(1, 151))
prices = [bn.binomial_option(100, 100, 1, 0.05, 0.2, steps=n) for n in steps]

plt.plot(steps, prices, linewidth=1, label="Binomial price")
plt.axhline(bs, color="black", linestyle="--", label=f"Black-Scholes {bs:.4f}")
plt.title("Binomial call price vs. number of steps")
plt.xlabel("Steps"); plt.ylabel("Call price")
plt.legend(); plt.grid(alpha=0.3)
plt.show()

for n in [5, 25, 100, 500]:
    print(f"{n:>4} steps: {bn.binomial_option(100, 100, 1, 0.05, 0.2, steps=n):.4f}")
```

The zig-zag between odd and even step counts is typical. Practitioners often average two adjacent step counts.

## American options: the value of early exercise

The big advantage of trees over formulas: they handle **American** options easily. At each node, compare continuing to hold with exercising immediately, and take the larger.

```python run
print(f"{'Strike':>6} {'European put':>13} {'American put':>13} {'Early-exercise premium':>23}")
for K in [90, 100, 110, 120]:
    euro = bn.binomial_option(100, K, 1, 0.06, 0.25, steps=300, kind="put")
    amer = bn.binomial_option(100, K, 1, 0.06, 0.25, steps=300, kind="put", american=True)
    print(f"{K:>6} {euro:>13.4f} {amer:>13.4f} {amer - euro:>23.4f}")
```

Deep in-the-money American puts are worth exercising early: receiving the strike now and earning interest on it beats waiting. For calls on non-dividend stocks, early exercise is never optimal, so American and European calls have the same price:

```python run
euro_call = bn.binomial_option(100, 100, 1, 0.06, 0.25, steps=300)
amer_call = bn.binomial_option(100, 100, 1, 0.06, 0.25, steps=300, american=True)
print(f"European call {euro_call:.4f}  American call {amer_call:.4f}")
```

## Key takeaways

- **Replication:** an option can be copied with \(\Delta\) shares and a bond, so it must cost the same as that portfolio.
- **Risk-neutral pricing:** value = discounted expected payoff using \(p = (e^{r\Delta t} - d)/(u - d)\), not real-world probabilities.
- **CRR trees** (\(u = e^{\sigma\sqrt{\Delta t}}\)) converge to Black-Scholes as steps increase.
- Trees handle **American** options: early exercise can be valuable for puts, never for calls on non-dividend stocks.

## Exercises

1. A stock at $50 will be $60 or $42 in 6 months. The risk-free rate is 4% (continuous). Price a put with K = $50 by replication.
2. Use a 200-step tree to price a 6-month American put with S = 40, K = 45, r = 5%, σ = 30%. What is the early-exercise premium?
3. Show the 3-step tree for an **American put** (S = 100, K = 110, r = 5%, σ = 20%). At which nodes is early exercise optimal?

<details>
<summary>Solutions</summary>

```python run
dlt, bnd, val = bn.one_step_replication(50, 60, 42, 50, 0.04, 0.5, kind="put")
print(f"1. Delta {dlt:.3f}, bond {bnd:.2f}, put value {val:.4f}")
e = bn.binomial_option(40, 45, 0.5, 0.05, 0.3, steps=200, kind="put")
a = bn.binomial_option(40, 45, 0.5, 0.05, 0.3, steps=200, kind="put", american=True)
print(f"2. European {e:.4f}, American {a:.4f}, premium {a - e:.4f}\n")
show_tree(100, 110, 1, 0.05, 0.2, 3, kind="put", american=True)
print("3. Early exercise is optimal wherever option value = 110 − stock price (the low-price nodes).")
```

</details>

## Watch & read

- [watch] [MIT 15.401 Finance Theory I](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/). The "Options" lectures build the binomial model from replication.
- [course] [MIT OCW 18.S096 Topics in Mathematics with Applications in Finance](https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/). Lectures on risk-neutral valuation and stochastic processes.
- [read] [Investopedia: Binomial Option Pricing Model](https://www.investopedia.com/terms/b/binomialoptionpricing.asp). Summary with a worked example.
- [course] [Coursera: Financial Engineering and Risk Management (Columbia)](https://www.coursera.org/specializations/financialengineering). Free-to-audit courses that go deep on binomial models and term-structure trees.
