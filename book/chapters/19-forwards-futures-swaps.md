# Forwards, Futures and Swaps

A farmer worries that wheat prices will fall before harvest. A bakery worries they'll rise. An airline worries about jet fuel, an exporter about exchange rates, a borrower about interest rates. **Derivatives** let each of them lock in a price today for a transaction in the future, transferring risk to someone more willing or able to bear it.

> [!IMPORTANT]
> Forward prices aren't forecasts. They're set by **no-arbitrage**: the forward price must equal the cost of buying the asset today and carrying it to the delivery date. If it didn't, traders could lock in riskless profits.

## Forward contracts

A **forward** is an agreement to buy (long) or sell (short) an asset at a fixed **delivery price** \(K\) on a future date \(T\). No money changes hands today. At expiry:

\[ \text{Long payoff} = S_T - K \qquad \text{Short payoff} = K - S_T \]

```python run
import matplotlib.pyplot as plt

K = 100
prices = list(range(60, 141))
plt.plot(prices, [s - K for s in prices], label="Long forward")
plt.plot(prices, [K - s for s in prices], label="Short forward")
plt.axhline(0, color="gray", linewidth=0.8)
plt.title(f"Forward payoffs at expiry (delivery price {K})")
plt.xlabel("Price of the asset at expiry"); plt.ylabel("Payoff")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

It's a zero-sum game: the long's gain is exactly the short's loss.

## Pricing a forward by no-arbitrage

Consider a stock worth $100 today that pays no dividends, and a 5% continuously compounded risk-free rate. What's the fair 1-year forward price?

**Cash-and-carry argument.** You could get the stock in one year in two ways:

1. Enter a long forward at price \(F\): pay \(F\) in one year.
2. Borrow $100 today, buy the stock, and hold it: repay \(100e^{0.05}\) in one year.

Both give you one share in a year with no cash today, so they must cost the same:

\[ F_0 = S_0\,e^{rT} \]

With income (dividends, foreign interest) at yield \(q\), or storage costs \(u\):

\[ F_0 = S_0\,e^{(r + u - q)T} \]

```python run
from finance101 import derivatives as d

print(f"Non-dividend stock: F = {d.forward_price(100, 0.05, 1):.2f}")
print(f"Stock index with 1.5% dividend yield: F = {d.forward_price(100, 0.05, 1, income_yield=0.015):.2f}")
print(f"Gold with 0.5% storage cost: F = {d.forward_price(2_000, 0.05, 1, storage_cost=0.005):,.2f}")
print(f"EUR/USD (spot 1.08, USD rate 5%, EUR rate 3%): F = {d.fx_forward(1.08, 0.05, 0.03, 1):.4f}")
```

### Exploiting a mispricing

Suppose the market quotes the 1-year forward at **$108** instead of the fair $105.13. Here is the arbitrage:

```python run
import math

S0, r, T, F_market = 100, 0.05, 1, 108.0
F_fair = d.forward_price(S0, r, T)

print(f"Fair forward {F_fair:.2f} < market {F_market:.2f}: forward is too expensive → sell it")
print("Today : borrow 100, buy the stock, short the forward at 108  → net cash 0")
print(f"Year 1: deliver the stock for {F_market:.2f}, repay loan {S0 * math.exp(r * T):.2f}")
print(f"Riskless profit: {F_market - S0 * math.exp(r * T):.2f} per share, whatever the stock price does")
```

Traders compete to do this until the market price returns to the fair value. That's why we can price forwards **without** knowing anything about expected returns or risk preferences.

### Valuing an existing forward

A forward is worth zero when it's signed. Later, as the spot price moves, it gains or loses value:

\[ f = S_0 e^{-qT} - K e^{-rT} \]

```python run
# Six months ago you agreed to buy at K = 105 in one year. Now S = 112, 6 months remain.
print(f"Value of your long forward: {d.forward_contract_value(112, 105, 0.05, 0.5):.2f}")
```

## Futures

**Futures** are standardized forwards traded on exchanges such as CME. The big difference is **daily settlement** (marking to market): gains and losses are paid every day through a **margin account**, so neither side can build up a large unpaid debt. A clearinghouse stands between buyer and seller and guarantees the trade.

```python run
import random

rng = random.Random(7)
initial_margin, maintenance_margin, contracts, multiplier = 12_000, 9_000, 1, 50
entry = 5_000.0                                       # an index future, $50 per point
settle = entry
balance = initial_margin
print(f"{'Day':>3} {'Settle':>9} {'Daily P&L':>10} {'Margin':>9}  Note")
for day in range(1, 11):
    new_settle = settle * (1 + rng.gauss(-0.003, 0.012))
    pnl = d.futures_pnl(settle, new_settle, contracts, multiplier)
    balance += pnl
    note = ""
    if balance < maintenance_margin:
        note = f"MARGIN CALL: deposit {initial_margin - balance:,.0f}"
        balance = initial_margin
    print(f"{day:>3} {new_settle:>9.1f} {pnl:>10,.0f} {balance:>9,.0f}  {note}")
    settle = new_settle
print(f"\nTotal P&L: {d.futures_pnl(entry, settle, contracts, multiplier):,.0f}")
```

> [!WARNING]
> Margin calls are where leverage bites. A position can be right in the long run and still be forced closed if you can't meet the daily calls. This is how several famous funds and companies have failed.

## Hedging with futures

An airline will buy 2 million gallons of jet fuel in three months. There's no jet fuel future, so it uses **heating oil futures**, which are highly correlated but not identical. The remaining mismatch is **basis risk**. The **minimum-variance hedge ratio** is

\[ h^* = \rho\,\frac{\sigma_S}{\sigma_F} \qquad \text{contracts} = \frac{h^* \times \text{exposure}}{\text{contract size}} \]

```python run
sigma_spot, sigma_fut, rho = 0.032, 0.035, 0.92          # monthly volatility of price changes
h = d.hedge_ratio(sigma_spot, sigma_fut, rho)
contracts = h * 2_000_000 / 42_000                        # heating oil contract = 42,000 gallons
print(f"Hedge ratio {h:.3f} → about {round(contracts)} contracts")

rng = random.Random(1)
unhedged, hedged = [], []
for _ in range(5_000):
    z1, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
    fut_change = sigma_fut * z1
    spot_change = sigma_spot * (rho * z1 + (1 - rho ** 2) ** 0.5 * z2)
    unhedged.append(-spot_change)                         # fuel gets more expensive → airline loses
    hedged.append(-spot_change + h * fut_change)          # long futures gain offsets it

import statistics
print(f"Volatility of fuel cost: unhedged {statistics.stdev(unhedged):.2%}, hedged {statistics.stdev(hedged):.2%}")
print(f"Risk reduction: {1 - statistics.variance(hedged) / statistics.variance(unhedged):.0%} of variance (= ρ² = {rho ** 2:.0%})")
```

## Interest-rate swaps

In a **plain vanilla interest-rate swap**, one party pays a **fixed** rate and receives a **floating** rate (such as SOFR) on a notional principal. A company with floating-rate debt can swap into fixed payments to remove its interest-rate risk.

A swap can be valued as the difference between two bonds:

- The **fixed leg** is like a fixed-coupon bond.
- The **floating leg** resets to market rates, so right after each payment it's worth par.

The **par swap rate** makes a new swap worth zero:

\[ s = \frac{1 - DF_n}{\sum_{i=1}^{n} DF_i \,/\, m} \]

```python run
from finance101 import yield_curve as yc

spot_curve = [0.040, 0.042, 0.044, 0.045, 0.046]
dfs = [yc.discount_factor(s, t) for t, s in enumerate(spot_curve, start=1)]
swap_rate = d.par_swap_rate(dfs)
print(f"5-year par swap rate: {swap_rate:.3%}")

# A year later rates have risen 1 percentage point. You receive fixed on $10m at the old rate, 4 years left.
new_dfs = [yc.discount_factor(s + 0.01, t) for t, s in enumerate(spot_curve[:4], start=1)]
value = d.swap_value_receive_fixed(10_000_000, swap_rate, new_dfs)
print(f"Value to the receive-fixed side after rates rise: ${value:,.0f}")
```

When rates rise, the party receiving fixed loses, because it's locked into the old, lower rate. That party is effectively **long a bond**.

## Key takeaways

- Forward and futures prices come from **no-arbitrage**: \(F = S e^{(r + u - q)T}\), not from forecasts.
- **Futures** settle daily through margin accounts, which removes counterparty risk but can force liquidation.
- The minimum-variance **hedge ratio** is \(\rho\,\sigma_S/\sigma_F\); hedging removes \(\rho^2\) of the variance, and the rest is basis risk.
- An **interest-rate swap** exchanges fixed for floating payments; value it as the difference between a fixed-rate bond and a floating-rate bond.

## Exercises

1. The S&P 500 is at 5,200, the 9-month risk-free rate is 4.5% and the dividend yield is 1.4% (both continuous). What is the fair futures price?
2. Spot USD/JPY is 150 (yen per dollar). The yen rate is 0.5% and the dollar rate is 4.5%. What is the 1-year forward? (Hint: treat yen as domestic: `fx_forward(150, 0.005, 0.045, 1)`.)
3. In the swap example, what happens to the receive-fixed value if rates **fall** by 1 point instead?

<details>
<summary>Solutions</summary>

```python run
print(f"1. {d.forward_price(5_200, 0.045, 0.75, income_yield=0.014):,.1f}")
print(f"2. {d.fx_forward(150, 0.005, 0.045, 1):.2f} yen per dollar (the dollar trades at a forward discount)")
down = [yc.discount_factor(s - 0.01, t) for t, s in enumerate(spot_curve[:4], start=1)]
print(f"3. ${d.swap_value_receive_fixed(10_000_000, swap_rate, down):,.0f}")
```

</details>

## Watch & read

- [watch] [Yale ECON 252 (Shiller), lecture "Forwards and Futures"](https://oyc.yale.edu/economics/econ-252). The history and economics of futures markets.
- [watch] [Khan Academy: Derivative securities](https://www.khanacademy.org/economics-finance-domain/core-finance/derivative-securities). Forwards, futures, swaps and margin explained step by step.
- [course] [CME Group Education](https://www.cmegroup.com/education.html). Free courses on futures and options from the world's largest futures exchange.
- [read] [Investopedia: Forward Contract](https://www.investopedia.com/terms/f/forwardcontract.asp) and [Swap](https://www.investopedia.com/terms/s/swap.asp). Quick references.
- [course] [MIT OCW 18.S096 Topics in Mathematics with Applications in Finance](https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/). Lectures by practitioners on derivatives and their mathematics.
