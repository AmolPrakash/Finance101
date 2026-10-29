# Financial Ratio Analysis

Is $50 million of profit good? For a corner bakery it would be extraordinary; for Apple it would be a disaster. Raw numbers depend on size. **Ratios** scale numbers so you can compare a company with its own past, with competitors, and with industry norms.

> [!IMPORTANT]
> Ratios answer four questions:
> 1. **Profitability:** how much does the firm earn on its sales and its capital?
> 2. **Liquidity:** can it pay its bills over the next year?
> 3. **Leverage (solvency):** how much does it rely on debt, and can it service that debt?
> 4. **Efficiency:** how hard do its assets work?
>
> Market ratios add a fifth question: **what are investors paying** for all of that?

We'll analyze two made-up retailers. **SteadyMart** is a conservative discount chain; **LeverLux** is a high-end boutique financed largely with debt.

```python run
from finance101.statements import (BalanceSheet, IncomeStatement, dupont,
                                   leverage_ratios, liquidity_ratios, profitability_ratios)

companies = {
    "SteadyMart": (
        IncomeStatement(revenue=10_000, cost_of_goods_sold=7_500, operating_expenses=1_900,
                        interest_expense=40, tax_expense=140),
        BalanceSheet(current_assets=2_600, inventory=1_500, total_assets=5_000,
                     current_liabilities=1_300, total_liabilities=1_800),
    ),
    "LeverLux": (
        IncomeStatement(revenue=4_000, cost_of_goods_sold=1_600, operating_expenses=1_700,
                        interest_expense=180, tax_expense=130),
        BalanceSheet(current_assets=1_400, inventory=900, total_assets=4_400,
                     current_liabilities=1_250, total_liabilities=3_400),
    ),
}

for name, (inc, bal) in companies.items():
    print(f"{name}: revenue {inc.revenue:,}, net income {inc.net_income:,}, equity {bal.equity:,}")
```

## 1. Profitability ratios

| Ratio | Formula | Tells you |
|---|---|---|
| Gross margin | Gross profit / Revenue | Pricing power and production cost |
| Operating margin | EBIT / Revenue | Profit from core operations |
| Net margin | Net income / Revenue | What's left for owners per $ of sales |
| Return on assets (ROA) | Net income / Total assets | How well assets generate profit |
| Return on equity (ROE) | Net income / Equity | Return on the owners' capital |

```python run
def show(title, func):
    rows = {name: func(inc, bal) for name, (inc, bal) in companies.items()}
    keys = next(iter(rows.values())).keys()
    print(f"{title:<20}" + "".join(f"{name:>14}" for name in rows))
    for k in keys:
        print(f"  {k:<18}" + "".join(f"{rows[name][k]:>14.3f}" for name in rows))

show("Profitability", profitability_ratios)
```

LeverLux has far fatter margins (luxury goods), yet the two firms earn almost the **same return on assets**, about 8.5–9%. LeverLux's **return on equity**, though, is three times higher. Why? Keep reading.

## 2. Liquidity ratios

\[ \text{Current ratio} = \frac{\text{Current assets}}{\text{Current liabilities}} \qquad \text{Quick ratio} = \frac{\text{Current assets} - \text{Inventory}}{\text{Current liabilities}} \]

The quick ratio excludes inventory because inventory can be hard to sell fast without big discounts.

```python run
show("Liquidity", lambda inc, bal: liquidity_ratios(bal))
```

A quick ratio well below 1 means the firm depends on selling inventory, or on new borrowing, to pay its near-term bills.

## 3. Leverage ratios

```python run
show("Leverage", leverage_ratios)
```

**Interest coverage** (EBIT / interest) shows how many times over the firm can pay its interest bill from operating profit. Lenders get nervous below about 3x. LeverLux would be in trouble if its sales fell even modestly.

## 4. Efficiency ratios

These measure how quickly the firm turns its assets into sales and cash. They need a few more inputs: receivables and payables.

\[ \text{Days sales outstanding (DSO)} = \frac{\text{Receivables}}{\text{Revenue}} \times 365 \qquad \text{Days inventory (DIO)} = \frac{\text{Inventory}}{\text{COGS}} \times 365 \]

\[ \text{Days payables (DPO)} = \frac{\text{Payables}}{\text{COGS}} \times 365 \qquad \text{Cash conversion cycle} = DIO + DSO - DPO \]

```python run
extra = {"SteadyMart": {"receivables": 150, "payables": 900},
         "LeverLux": {"receivables": 300, "payables": 250}}

for name, (inc, bal) in companies.items():
    dso = extra[name]["receivables"] / inc.revenue * 365
    dio = bal.inventory / inc.cost_of_goods_sold * 365
    dpo = extra[name]["payables"] / inc.cost_of_goods_sold * 365
    print(f"{name:<11} asset turnover {inc.revenue / bal.total_assets:4.2f}x | "
          f"DSO {dso:5.1f}  DIO {dio:5.1f}  DPO {dpo:5.1f}  → cash cycle {dio + dso - dpo:6.1f} days")
```

SteadyMart sells its inventory fast and collects cash almost immediately, so each dollar is tied up for only about a month. LeverLux's inventory sits for over 200 days, and its cash is tied up for almost six months.

## The DuPont decomposition

Why do two firms with nearly the same ROA earn such different ROEs? **DuPont analysis** splits ROE into three drivers:

\[ ROE = \underbrace{\frac{\text{Net income}}{\text{Revenue}}}_{\text{net margin}} \times \underbrace{\frac{\text{Revenue}}{\text{Assets}}}_{\text{asset turnover}} \times \underbrace{\frac{\text{Assets}}{\text{Equity}}}_{\text{equity multiplier}} \]

```python run
import matplotlib.pyplot as plt

parts = ["net_margin", "asset_turnover", "equity_multiplier"]
fig, axes = plt.subplots(1, 3, figsize=(10, 3))
for ax, part in zip(axes, parts):
    values = [dupont(inc, bal)[part] for inc, bal in companies.values()]
    ax.bar(list(companies), values, color=["#2f7d6b", "#8a4b0f"])
    ax.set_title(part.replace("_", " "))
plt.tight_layout()
plt.show()

for name, (inc, bal) in companies.items():
    d = dupont(inc, bal)
    print(f"{name:<11} ROE {d['return_on_equity']:.1%} = {d['net_margin']:.1%} × {d['asset_turnover']:.2f} × {d['equity_multiplier']:.2f}")
```

SteadyMart earns its returns through **turnover**: thin margins on huge volume. LeverLux makes up for slow turnover with **margins**, which is why the ROAs match, and then multiplies its ROA by an equity multiplier of 4.4. Leverage triples its ROE, but it also makes that ROE fragile: a modest drop in sales could wipe out its profit (see Exercise 1). A high ROE is not automatically a good one.

## 5. Market (valuation) ratios

These combine the statements with the share price:

| Ratio | Formula | Meaning |
|---|---|---|
| Price/Earnings (P/E) | Price per share / EPS | $ paid per $1 of annual earnings |
| Price/Book (P/B) | Market cap / Book equity | Premium over accounting net worth |
| EV/EBITDA | (Market cap + Debt − Cash) / EBITDA | Value of the whole business vs. operating cash earnings |
| Dividend yield | Dividends per share / Price | Cash income return |

```python run
shares = 250          # millions of shares, SteadyMart
price = 42.00
net_income = companies["SteadyMart"][0].net_income
equity = companies["SteadyMart"][1].equity
eps = net_income / shares

print(f"EPS  ${eps:.2f}")
print(f"P/E  {price / eps:.1f}x")
print(f"P/B  {price * shares / equity:.2f}x")
```

We'll see in Chapter 11 how a P/E multiple connects to growth and risk.

## Using ratios well

> [!WARNING]
> - **Compare like with like.** A software company and a grocery chain have completely different "normal" ratios.
> - **Look at trends.** One year is a snapshot; five years tell a story.
> - **Watch the denominators.** Ratios built on negative equity or tiny earnings explode into meaningless numbers.
> - **Accounting choices matter.** Lease treatment, depreciation methods and one-off charges can move ratios a lot.

## Key takeaways

- Ratios make companies of different sizes comparable.
- Profitability (margins, ROA, ROE), liquidity (current, quick), leverage (D/E, coverage), efficiency (turnover, days) and market ratios (P/E, P/B, EV/EBITDA) each answer a different question.
- **DuPont:** ROE = margin × turnover × leverage. A high ROE driven by leverage is riskier than one driven by margins or turnover.

## Exercises

1. LeverLux's revenue drops 20% while COGS stays at 40% of revenue and other expenses are unchanged. Recompute its net income and interest coverage (keep taxes at 25% of pre-tax profit, and zero if pre-tax profit is negative).
2. What would SteadyMart's ROE be if it borrowed 1,000 more and used it to buy back shares (equity falls by 1,000, interest rises by 50, ignore the tax effect on interest)?
3. Download a real company's 10-K from EDGAR and compute five ratios in the scratchpad.

<details>
<summary>Solutions</summary>

```python run
inc, bal = companies["LeverLux"]
rev = inc.revenue * 0.8
ebit = rev - 0.4 * rev - inc.operating_expenses
ebt = ebit - inc.interest_expense
ni = ebt - max(ebt, 0) * 0.25
print(f"1. LeverLux after a 20% sales drop: EBIT {ebit:,.0f}, net income {ni:,.0f}, coverage {ebit / inc.interest_expense:.2f}x")

inc, bal = companies["SteadyMart"]
new_ni = inc.net_income - 50
print(f"2. SteadyMart ROE after leveraged buyback: {new_ni / (bal.equity - 1_000):.1%}  (was {inc.net_income / bal.equity:.1%})")
```

</details>

## Watch & read

- [watch] [Aswath Damodaran's YouTube channel](https://www.youtube.com/@AswathDamodaranonValuation). The NYU professor's free lectures on accounting for valuation, including how to read statements critically.
- [read] [OpenStax *Principles of Finance*, Chapter 6: Measures of Financial Health](https://openstax.org/details/books/principles-finance). Ratio analysis with worked examples.
- [read] [Investopedia: Ratio Analysis](https://www.investopedia.com/terms/r/ratioanalysis.asp). Definitions of every common ratio.
- [data] [Damodaran Online: industry data](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datacurrent.html). Free, updated industry averages for margins, multiples and more. Great for "is this ratio normal?"
- [course] [Corporate Finance Institute free resources](https://corporatefinanceinstitute.com/resources/). Practical guides to financial analysis and modeling.
