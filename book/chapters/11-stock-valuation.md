# Stock Valuation

A share of stock is a claim on a company's future cash flows. Unlike a bond, nothing is promised: dividends can rise, fall or disappear, and there's no maturity date. Valuing a stock therefore means **forecasting** cash flows and **discounting** them at a rate that reflects their risk. This chapter covers the two main approaches: discounted cash flow models and relative valuation with multiples.

> [!IMPORTANT]
> A stock is worth the present value of all the cash it will ever pay its owners. Every valuation model, from the dividend discount model to a 50-tab Wall Street spreadsheet, is a way of estimating that present value.

## Where stock returns come from

If you buy a share at \(P_0\), receive a dividend \(D_1\) and sell at \(P_1\) a year later, your return is

\[ r = \underbrace{\frac{D_1}{P_0}}_{\text{dividend yield}} + \underbrace{\frac{P_1 - P_0}{P_0}}_{\text{capital gain}} \]

Rearranging gives today's price: \(P_0 = \frac{D_1 + P_1}{1 + r}\). But \(P_1\) depends on \(D_2\) and \(P_2\), and so on forever. Substituting repeatedly gives the **dividend discount model (DDM)**:

\[ P_0 = \sum_{t=1}^{\infty} \frac{D_t}{(1 + r)^t} \]

Even investors who plan to sell in a year are, indirectly, paying for the whole future stream of dividends.

## The constant-growth (Gordon) model

If dividends grow at a constant rate \(g\) forever, the infinite sum collapses to a growing perpetuity:

\[ P_0 = \frac{D_1}{r - g} \qquad (r > g) \]

```python run
from finance101 import equity

d1, r, g = 2.40, 0.09, 0.04
print(f"Value per share: ${equity.gordon_growth_value(d1, r, g):.2f}")
```

The model is simple but surprisingly sensitive. Look at how the value changes with small changes in \(r\) and \(g\):

```python run
rates = [0.08, 0.09, 0.10, 0.11]
growths = [0.02, 0.03, 0.04, 0.05, 0.06]
print("r \\ g  " + "".join(f"{gg:>9.0%}" for gg in growths))
for rr in rates:
    print(f"{rr:>5.0%}  " + "".join(f"{equity.gordon_growth_value(d1, rr, gg):>9.2f}" for gg in growths))
```

> [!WARNING]
> As \(g\) approaches \(r\), the value explodes. Treat the Gordon model's output as a **range**, never a precise number, and never use a perpetual growth rate above the long-run growth of the economy (roughly 2–4% nominal).

### Turning it around: the market's expected return

Rearranging the model shows the return the market expects:

\[ r = \frac{D_1}{P_0} + g \]

```python run
price = 60.00
print(f"Implied expected return: {equity.implied_required_return(price, d1, g):.2%}  (dividend yield {d1 / price:.2%} + growth {g:.0%})")
```

## Where does growth come from?

A firm grows its dividends by **reinvesting** earnings. If it retains a fraction \(b\) of earnings (the **plowback ratio**) and earns a return on equity \(ROE\) on that reinvestment, then:

\[ g = b \times ROE \]

But growth isn't automatically good. It creates value only if the firm earns **more than investors require** on the money it reinvests:

```python run
eps1, r = 5.00, 0.10
print("Plowback   ROE     g      Price   P/E")
for roe in [0.08, 0.10, 0.15]:
    for b in [0.0, 0.3, 0.6]:
        growth = b * roe
        dividend = eps1 * (1 - b)
        price = equity.gordon_growth_value(dividend, r, growth)
        print(f"  {b:>4.0%}   {roe:>5.0%}  {growth:>5.1%}  {price:>8.2f}  {price / eps1:>5.1f}")
    print()
```

- When ROE **=** r (10%), reinvesting doesn't change the price at all.
- When ROE **<** r (8%), reinvesting **destroys** value. The firm grows, but shareholders would be better off with the dividends.
- When ROE **>** r (15%), reinvesting **creates** value.

### Present value of growth opportunities (PVGO)

You can split any stock price into the value of current earnings (as if they were paid out forever with no growth) plus the value of future growth:

\[ P_0 = \frac{EPS_1}{r} + PVGO \]

```python run
for name, price, eps in [("Utility", 52.0, 4.50), ("Tech growth stock", 180.0, 3.00)]:
    no_growth_value = eps / 0.09
    print(f"{name:<18} price ${price:>6.2f} = no-growth value ${no_growth_value:>6.2f} + PVGO ${price - no_growth_value:>7.2f} ({(price - no_growth_value) / price:.0%} of price)")
```

## Where P/E ratios come from

Divide the Gordon formula by next year's earnings:

\[ \frac{P_0}{EPS_1} = \frac{\text{payout ratio}}{r - g} \]

A high P/E signals that investors expect **high growth** or see **low risk** (a low \(r\)), or both. It's not automatically "expensive".

## Two-stage growth

Young companies often grow quickly for a few years, then settle down. A **two-stage DDM** values the high-growth dividends explicitly, then adds a Gordon-model **terminal value** for everything after:

\[ P_0 = \sum_{t=1}^{N} \frac{D_0 (1 + g_1)^t}{(1 + r)^t} + \frac{1}{(1+r)^N}\cdot\frac{D_{N+1}}{r - g_2} \]

```python run
value = equity.two_stage_ddm(current_dividend=1.20, required_return=0.10, high_growth=0.18,
                             high_growth_years=5, terminal_growth=0.035)
print(f"Two-stage value: ${value:.2f}")
```

## Free cash flow valuation (DCF)

Many companies pay small or no dividends: they buy back shares or reinvest everything. Analysts therefore usually value the **whole firm** by discounting its **free cash flow to the firm (FCFF)** at the **weighted average cost of capital (WACC)** (Chapter 12), then subtract debt to get equity value:

1. Forecast FCF for 5–10 years.
2. Add a **terminal value** for the years after: \(TV_N = \frac{FCF_{N+1}}{WACC - g}\).
3. Discount everything at WACC → **enterprise value**.
4. Subtract net debt (debt minus cash) → **equity value**; divide by shares outstanding → **value per share**.

```python run
fcf = [410, 455, 500, 540, 575]          # $ millions, years 1-5
wacc, terminal_growth = 0.085, 0.03
net_debt, shares = 1_200, 150           # $ millions, millions of shares

enterprise_value = equity.dcf_value(fcf, wacc, terminal_growth)
pv_explicit = sum(cf / (1 + wacc) ** t for t, cf in enumerate(fcf, start=1))
equity_value = enterprise_value - net_debt

print(f"PV of years 1-5 FCF : ${pv_explicit:>8,.0f}m")
print(f"PV of terminal value: ${enterprise_value - pv_explicit:>8,.0f}m  ({1 - pv_explicit / enterprise_value:.0%} of the total!)")
print(f"Enterprise value    : ${enterprise_value:>8,.0f}m")
print(f"Equity value        : ${equity_value:>8,.0f}m")
print(f"Value per share     : ${equity_value / shares:>8.2f}")
```

Most of a DCF's value usually sits in the terminal value. That's why analysts always show a **sensitivity table**:

```python run
print("WACC \\ g  " + "".join(f"{gg:>9.1%}" for gg in [0.02, 0.025, 0.03, 0.035, 0.04]))
for w in [0.075, 0.08, 0.085, 0.09, 0.095]:
    row = [(equity.dcf_value(fcf, w, gg) - net_debt) / shares for gg in [0.02, 0.025, 0.03, 0.035, 0.04]]
    print(f"{w:>7.1%}   " + "".join(f"{v:>9.2f}" for v in row))
```

## Relative valuation: multiples

Instead of forecasting cash flows, you can price a company **relative to similar companies**: if peers trade at 18 times earnings, a similar firm should too.

```python run
import statistics

peers = {"Peer A": 17.5, "Peer B": 21.0, "Peer C": 15.8, "Peer D": 19.2}
target_eps = 4.10
median_pe = statistics.median(peers.values())
print(f"Median peer P/E: {median_pe:.1f}x → implied price ${median_pe * target_eps:.2f}")
print(f"Range: ${min(peers.values()) * target_eps:.2f} to ${max(peers.values()) * target_eps:.2f}")
```

Multiples are fast and reflect current market sentiment, but they assume the peers are fairly priced and truly comparable. In practice, analysts use **both** a DCF and multiples and investigate when they disagree.

## Key takeaways

- A stock is worth the PV of its future cash flows to shareholders.
- **Gordon model:** \(P_0 = D_1/(r - g)\); very sensitive to \(r - g\).
- Growth (\(g = b \times ROE\)) adds value only when **ROE > r**.
- P/E = payout / (r − g): high multiples reflect growth or low risk.
- **DCF:** discount FCF at WACC, add a terminal value, subtract net debt. The terminal value usually dominates.
- **Multiples** value a firm relative to peers; use them alongside a DCF.

## Exercises

1. A stock just paid a $3.00 dividend (\(D_0\)), which is expected to grow 5% forever. If investors require 11%, what is it worth? (Careful: \(D_1 = D_0(1+g)\).)
2. A stock trades at $45 with an expected dividend of $1.80 and expected growth of 6%. What return does the market expect?
3. In the DCF above, what terminal growth rate makes the value per share $40?
4. A firm earns EPS of $6, pays out 30%, and has ROE of 12%. Investors require 10%. What are its growth rate, price and PVGO?

<details>
<summary>Solutions</summary>

```python run
print(f"1. ${equity.gordon_growth_value(3.00 * 1.05, 0.11, 0.05):.2f}")
print(f"2. {equity.implied_required_return(45, 1.80, 0.06):.2%}")
low, high = 0.0, 0.08
for _ in range(60):
    mid = (low + high) / 2
    low, high = (mid, high) if (equity.dcf_value(fcf, wacc, mid) - net_debt) / shares < 40 else (low, mid)
print(f"3. Terminal growth for $40/share: {mid:.2%}")
g4 = 0.7 * 0.12
p4 = equity.gordon_growth_value(6 * 0.3, 0.10, g4)
print(f"4. g = {g4:.1%}, price ${p4:.2f}, PVGO ${p4 - 6 / 0.10:.2f}")
```

</details>

## Watch & read

- [watch] [Aswath Damodaran's valuation lectures (YouTube)](https://www.youtube.com/@AswathDamodaranonValuation). The best free valuation course anywhere, from the "Dean of Valuation".
- [data] [Damodaran Online](https://pages.stern.nyu.edu/~adamodar/). Free spreadsheets, datasets (industry multiples, betas, cost of capital) and lecture notes.
- [read] [OpenStax *Principles of Finance*, Chapter 11: Stocks and Stock Valuation](https://openstax.org/details/books/principles-finance). DDM and multiples with practice problems.
- [read] [Investopedia: Dividend Discount Model](https://www.investopedia.com/terms/d/ddm.asp). A short reference.
- [read] [Damodaran's blog, *Musings on Markets*](https://aswathdamodaran.blogspot.com/). Real valuations of real companies, explained step by step.
