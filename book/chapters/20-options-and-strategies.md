# Options and Option Strategies

A forward *obliges* you to trade. An **option** gives you the **right, but not the obligation**. That asymmetry, keeping the upside while limiting the downside, is what makes options so useful for insurance and speculation alike, and so interesting to price.

> [!IMPORTANT]
> - A **call** is the right to **buy** at the strike price \(K\). Payoff: \(\max(S_T - K, 0)\).
> - A **put** is the right to **sell** at \(K\). Payoff: \(\max(K - S_T, 0)\).
>
> Because the holder can walk away, payoffs are never negative, so options always cost something up front: the **premium**.

## Terminology

| Term | Meaning |
|---|---|
| **Strike (exercise) price** \(K\) | The price at which the option holder can buy or sell |
| **Expiration** \(T\) | The last date the option can be exercised |
| **European / American** | Exercisable only at expiry / any time before expiry |
| **In / at / out of the money** | Exercising now would be profitable / break-even / unprofitable |
| **Intrinsic value** | What the option would be worth if exercised now: \(\max(S - K, 0)\) for a call |
| **Time value** | Premium minus intrinsic value: the value of the chance of further favorable moves |

## Payoff and profit diagrams

**Payoff** is what you receive at expiry; **profit** subtracts the premium you paid (or adds the premium you received if you sold the option).

```python run
import matplotlib.pyplot as plt
from finance101 import options as opt

K, call_premium, put_premium = 100, 8.0, 6.0
S = list(range(60, 141))

fig, axes = plt.subplots(2, 2, figsize=(9, 6.5), sharex=True)
cases = [
    ("Long call", [opt.call_payoff(s, K) - call_premium for s in S]),
    ("Short call", [call_premium - opt.call_payoff(s, K) for s in S]),
    ("Long put", [opt.put_payoff(s, K) - put_premium for s in S]),
    ("Short put", [put_premium - opt.put_payoff(s, K) for s in S]),
]
for ax, (title, profit) in zip(axes.flat, cases):
    ax.plot(S, profit)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_title(title); ax.grid(alpha=0.3)
for ax in axes[1]:
    ax.set_xlabel("Stock price at expiry")
plt.suptitle(f"Profit at expiry (K = {K}, call premium {call_premium}, put premium {put_premium})")
plt.tight_layout()
plt.show()
```

Notice the asymmetry: a long call can lose at most its premium but gain without limit. A **short** call earns a small premium but faces unlimited losses.

## Option strategies

Combining options, and sometimes stock, creates almost any payoff shape. The `strategy_payoff` function adds up the legs; we subtract the net premium to get the profit. Premiums below come from the Black-Scholes model (Chapter 22), with the stock at 100, 3 months to expiry, a 4% rate and 25% volatility.

```python run
spot, T, r, vol = 100, 0.25, 0.04, 0.25
call = lambda k: opt.black_scholes_call(spot, k, T, r, vol)
put = lambda k: opt.black_scholes_put(spot, k, T, r, vol)

strategies = {   # legs: (kind, strike, quantity); cost: net premium paid today
    "Covered call\n(own stock, sell 110 call)": ([("stock", None, 1), ("call", 110, -1)], spot - call(110)),
    "Protective put\n(own stock, buy 90 put)": ([("stock", None, 1), ("put", 90, 1)], spot + put(90)),
    "Bull call spread\n(buy 95 call, sell 110 call)": ([("call", 95, 1), ("call", 110, -1)], call(95) - call(110)),
    "Long straddle\n(buy 100 call + 100 put)": ([("call", 100, 1), ("put", 100, 1)], call(100) + put(100)),
    "Collar\n(stock + 90 put − 110 call)": ([("stock", None, 1), ("put", 90, 1), ("call", 110, -1)], spot + put(90) - call(110)),
    "Butterfly\n(90/100/110 calls, 1/−2/1)": ([("call", 90, 1), ("call", 100, -2), ("call", 110, 1)], call(90) - 2 * call(100) + call(110)),
}

fig, axes = plt.subplots(2, 3, figsize=(11, 6.5), sharex=True)
for ax, (name, (legs, cost)) in zip(axes.flat, strategies.items()):
    ax.plot(S, [opt.strategy_payoff(s, legs) - cost for s in S])
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_title(name, fontsize=9); ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()

for name, (legs, cost) in strategies.items():
    print(f"{name.splitlines()[0]:<17} net cost {cost:7.2f}")
```

| Strategy | View / purpose |
|---|---|
| **Covered call** | Own the stock, sell upside for income. Neutral to mildly bullish |
| **Protective put** | Insurance: floor on losses, keep the upside |
| **Bull call spread** | Bullish, but cheaper than a call because you give up gains above the upper strike |
| **Straddle** | Expect a **big move**, direction unknown (e.g. before earnings) |
| **Collar** | Cheap insurance: fund the put by selling upside |
| **Butterfly** | Expect the price to stay **near the middle strike** |

> [!TIP]
> Try building a **strangle** (buy a 90 put and a 110 call) or an **iron condor** in the scratchpad. Copy the strategies cell and add an entry.

## Put-call parity

Consider two portfolios:

- **A:** one call plus cash worth \(Ke^{-rT}\) (a zero-coupon bond paying \(K\) at expiry)
- **B:** one put plus one share

At expiry, both are worth \(\max(S_T, K)\). Since they have identical payoffs, they must have the same price today:

\[ C + K e^{-rT} = P + S \]

```python run
import math

c, p = call(100), put(100)
print(f"Call {c:.4f} + PV(K) {100 * math.exp(-r * T):.4f} = {c + 100 * math.exp(-r * T):.4f}")
print(f"Put  {p:.4f} + stock {spot:.4f}         = {p + spot:.4f}")
print(f"Put implied by parity: {opt.put_call_parity_put(c, spot, 100, T, r):.4f}")
```

Parity holds regardless of any model. It relies only on no-arbitrage. If it's violated, buy the cheap side and sell the expensive side for a riskless profit.

```python run
# Suppose the market quotes the put at 4.10 instead of the parity value. Try 4.90 too.
market_put = 4.10
parity_put = opt.put_call_parity_put(c, spot, 100, T, r)
if market_put < parity_put:
    print(f"Put is cheap ({market_put:.2f} < {parity_put:.2f}): buy put + buy stock, sell call, borrow PV(K)")
else:
    print(f"Put is rich ({market_put:.2f} > {parity_put:.2f}): sell put + short stock, buy call, lend PV(K)")
print(f"Profit today: {abs(parity_put - market_put):.2f}, and the positions cancel exactly at expiry")
```

## Bounds and the value of waiting

Arbitrage also sets bounds on option prices. For a European call on a non-dividend stock:

\[ \max(S - Ke^{-rT}, 0) \le C \le S \]

```python run
print(f"{'Spot':>5} {'Intrinsic':>10} {'Lower bound':>12} {'Call price':>11} {'Time value':>11}")
for s in [80, 90, 100, 110, 120]:
    price = opt.black_scholes_call(s, 100, T, r, vol)
    intrinsic = max(s - 100, 0)
    print(f"{s:>5} {intrinsic:>10.2f} {max(s - 100 * math.exp(-r * T), 0):>12.2f} {price:>11.2f} {price - intrinsic:>11.2f}")
```

Time value is largest **at the money**, where uncertainty about finishing in or out of the money is greatest. A consequence: an American call on a non-dividend-paying stock should **never be exercised early**. Selling it is always worth more than exercising, because exercising throws away the time value.

## Key takeaways

- Calls pay \(\max(S - K, 0)\), puts pay \(\max(K - S, 0)\); buyers pay a premium for the right without the obligation.
- Combining options and stock creates strategies for any view: covered calls, protective puts, spreads, straddles, collars, butterflies.
- **Put-call parity** \(C + Ke^{-rT} = P + S\) holds by no-arbitrage alone.
- Option value = intrinsic value + time value; time value peaks at the money.

## Exercises

1. You own a stock at $50 and buy a $45 put for $1.20. What is your maximum loss, and at what stock price do you break even at expiry?
2. A 3-month call (K = 50) costs $3.10, the stock is at $51 and r = 5%. What should a 3-month put with the same strike cost?
3. Plot the profit of a **short straddle** (sell the 100 call and the 100 put). When does it make money?

<details>
<summary>Solutions</summary>

```python run
print("1. Max loss = 50 − 45 + 1.20 = 6.20; break-even at 51.20")
print(f"2. Put = {opt.put_call_parity_put(3.10, 51, 50, 0.25, 0.05):.2f}")
premium = call(100) + put(100)
plt.plot(S, [premium - opt.strategy_payoff(s, [("call", 100, 1), ("put", 100, 1)]) for s in S])
plt.axhline(0, color="gray"); plt.title("Short straddle profit"); plt.show()
print(f"3. Profitable if the stock ends between {100 - premium:.2f} and {100 + premium:.2f}")
```

</details>

## Watch & read

- [watch] [Khan Academy: Derivative securities (options)](https://www.khanacademy.org/economics-finance-domain/core-finance/derivative-securities). Calls, puts, payoff diagrams and put-call parity.
- [watch] [Yale ECON 252 (Shiller), lecture "Options Markets"](https://oyc.yale.edu/economics/econ-252). Why option markets exist and how they're used.
- [course] [Options Industry Council (OIC)](https://www.optionseducation.org/). Free, non-commercial courses and strategy guides from the options industry's education body.
- [read] [Investopedia: Options basics](https://www.investopedia.com/options-basics-tutorial-4583012). A tutorial covering every strategy above.
