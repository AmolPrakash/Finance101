# What Finance Is and How the Financial System Works

Finance is the study of how people, companies and governments **move money across time and across risk**. A student borrows today against future earnings. A company raises money now to build a factory that pays off for decades. A retiree turns a lifetime of savings into a monthly income. Each of these trades money now for money later, under uncertainty.

> [!IMPORTANT]
> Almost every question in finance comes down to two things: **when** cash arrives, and **how sure** we are that it will arrive. The rest of this book gives you the tools to put a price on both.

## The three (and a half) branches of finance

| Branch | The central question | Where in this book |
|---|---|---|
| **Corporate finance** | Which projects should a firm invest in, and how should it pay for them? | FIN 102 |
| **Investments** | How should savers choose and combine assets, and how are those assets priced? | FIN 201 |
| **Financial markets & institutions** | How do banks, exchanges and funds connect savers to borrowers? | This chapter, FIN 202 |
| **Personal finance** | How should a household save, borrow, insure and invest? | Chapter 7 |

## Five ideas that run through everything

1. **The time value of money.** A dollar today is worth more than a dollar tomorrow, because today's dollar can be invested. (Chapters 2–4.)
2. **Risk and return go together.** Investors only accept more risk if they expect more return. (Chapters 14–16.)
3. **Cash is what matters.** Value comes from cash flows, not accounting profits. (Chapters 5, 9.)
4. **Markets are competitive.** Easy profits get competed away, so prices usually reflect available information. Free lunches are rare. (Chapter 16.)
5. **No arbitrage.** Two ways of getting the same future cash flows must cost the same today. If they didn't, someone would buy the cheap one, sell the expensive one, and pocket a riskless profit. (Chapters 19–22.)

## The financial system: connecting savers and borrowers

Some people have more money than they need right now (**savers**). Others have good uses for money they don't yet have (**borrowers**: entrepreneurs, home buyers, governments). The financial system moves money from the first group to the second through two channels:

- **Directly, through financial markets.** A company sells shares or bonds to investors. The investor owns a claim on the company directly.
- **Indirectly, through financial intermediaries.** You deposit money in a bank; the bank lends it to a home buyer. You own a claim on the bank, and the bank owns the claim on the borrower.

```
          ┌──────────── financial markets (stocks, bonds) ────────────┐
          │                                                           ▼
 SAVERS ──┤                                                       BORROWERS
 households│                                                     firms, home buyers,
 firms     └── intermediaries (banks, funds, insurers, pensions) ──► governments
```

### Types of markets

| Distinction | Meaning | Example |
|---|---|---|
| **Primary vs. secondary** | New securities sold by the issuer vs. existing securities traded between investors | An IPO vs. buying Apple shares on the Nasdaq |
| **Money vs. capital markets** | Short-term debt (under 1 year) vs. long-term debt and equity | Treasury bills vs. 30-year bonds and stocks |
| **Exchange vs. over-the-counter (OTC)** | Centralized trading with standard contracts vs. dealer networks with custom deals | NYSE stocks vs. most corporate bonds and swaps |
| **Debt vs. equity** | A fixed promise to repay vs. ownership of whatever is left over | A bond vs. a share |

### The main financial instruments

- **Debt** (loans, bonds, mortgages): the borrower promises fixed payments. Lenders get paid first but their upside is capped.
- **Equity** (stocks): owners get the *residual*, whatever remains after everyone else is paid. Unlimited upside, but last in line.
- **Derivatives** (forwards, futures, options, swaps): contracts whose value depends on another asset. Used to hedge or take on risk. (FIN 202.)

### Who the intermediaries are

| Institution | What it does | Why it adds value |
|---|---|---|
| Commercial banks | Take deposits, make loans | Screen and monitor borrowers; turn short-term deposits into long-term loans |
| Investment banks | Help firms issue securities, advise on mergers | Expertise and distribution to investors |
| Mutual funds & ETFs | Pool savers' money into diversified portfolios | Cheap diversification for small investors |
| Insurance companies | Collect premiums, pay claims | **Pool** risks that are ruinous alone but predictable in aggregate |
| Pension funds | Invest retirement savings | Long horizon, professional management |
| Central bank (e.g. the Federal Reserve) | Sets short-term interest rates, lender of last resort | Price stability and financial stability |

## Seeing risk pooling in action

Why does insurance work? A single house has, say, a 1-in-200 chance of burning down in a year. For one homeowner, that is a catastrophic, unpredictable risk. For an insurer with 100,000 houses, the number of fires each year is very predictable. This is the **law of large numbers**, and it's one of the oldest ideas in finance.

Run this cell, then change `houses` to 100 and run it again:

```python run
import random

def simulate_fires(houses, p_fire=0.005, years=10, seed=1):
    """Fraction of houses that burn each year, for several simulated years."""
    rng = random.Random(seed)
    return [sum(rng.random() < p_fire for _ in range(houses)) / houses for _ in range(years)]

houses = 100_000
rates = simulate_fires(houses)
print(f"Expected fire rate: 0.50%")
for year, r in enumerate(rates, start=1):
    print(f"Year {year:>2}: {r:.3%}")
```

With 100,000 houses, the yearly fire rate barely moves, so the insurer can set a premium of roughly 0.5% of the house value plus costs and stay solvent. With 100 houses the rate jumps around wildly, and one bad year could bankrupt the insurer.

## How a bank makes money

A bank borrows short (deposits) and lends long (mortgages, business loans). Its core profit is the **net interest margin**: the gap between what it earns on loans and what it pays on deposits.

```python run
deposits = 900_000_000        # what customers have deposited
equity = 100_000_000          # owners' capital
loans = 850_000_000           # money lent out
reserves = deposits + equity - loans   # cash and safe securities

deposit_rate = 0.02
loan_rate = 0.065
default_loss_rate = 0.008     # fraction of loans lost to defaults each year
operating_costs = 15_000_000

interest_income = loans * loan_rate + reserves * 0.04
interest_expense = deposits * deposit_rate
profit = interest_income - interest_expense - loans * default_loss_rate - operating_costs

print(f"Interest income : ${interest_income:>14,.0f}")
print(f"Interest expense: ${interest_expense:>14,.0f}")
print(f"Profit          : ${profit:>14,.0f}")
print(f"Return on equity: {profit / equity:.1%}")
```

> [!TIP]
> Change `default_loss_rate` to `0.04`, the kind of loss rate a bank with risky loans can suffer in a deep recession. A bank's equity is a thin cushion. Leverage, here $9 of deposits for every $1 of equity, boosts returns in good times and wipes owners out in bad ones. That is why banks are tightly regulated.

## The goal of the firm and the agency problem

Finance usually assumes a company should **maximize the value of the firm for its owners**, which means maximizing the present value of future cash flows to shareholders, not this quarter's profit.

But managers run the firm, and they aren't the owners. This conflict is the **agency problem**: managers might build empires, avoid risky-but-valuable projects to protect their jobs, or enjoy perks. Boards of directors, stock-based pay, takeover threats and disclosure rules all exist to keep managers aligned with owners.

## Key takeaways

- Finance is about valuing cash flows that differ in **timing** and **risk**.
- Savers reach borrowers directly through **markets** or indirectly through **intermediaries**.
- Debt holders get fixed claims and are paid first; equity holders get the residual.
- Intermediaries add value by **pooling**, **screening**, **diversifying** and **transforming maturities**, but leverage makes them fragile.

## Exercises

1. In the fire simulation, how many houses does an insurer need before the yearly fire rate stays within 0.45% to 0.55% every year? Experiment.
2. In the bank example, what loan default rate makes the bank's profit exactly zero?
3. Classify each as primary or secondary, money or capital market: (a) buying a 3-month Treasury bill at the government's auction, (b) selling your shares of an index ETF, (c) a startup's IPO.

<details>
<summary>Solutions</summary>

```python run
# 1. Try increasing sizes until all simulated years land within the band
for n in [1_000, 10_000, 100_000, 300_000]:
    r = simulate_fires(n, years=10)
    print(f"{n:>7} houses: min {min(r):.3%}, max {max(r):.3%}")

# 2. Break-even default rate: profit = 0
breakeven = (interest_income - interest_expense - operating_costs) / loans
print(f"Break-even default loss rate: {breakeven:.2%}")
```

3. (a) Primary, money market. (b) Secondary, capital market. (c) Primary, capital market.

</details>

## Watch & read

- [watch] [Yale ECON 252: Financial Markets (Robert Shiller)](https://oyc.yale.edu/economics/econ-252). Lectures 1–3 cover the purpose of finance, risk pooling and financial technology. Free, with transcripts.
- [course] [Coursera: Financial Markets (Yale, Shiller)](https://www.coursera.org/learn/financial-markets-global). The same material as a structured online course; free to audit.
- [watch] [Khan Academy: Money, banking and central banks](https://www.khanacademy.org/economics-finance-domain/core-finance/money-and-banking). Short videos on how banks create money and what the Fed does.
- [read] [OpenStax *Principles of Finance*, Chapters 1–3](https://openstax.org/details/books/principles-finance). Introduction to finance, corporate structure and governance, and economic foundations.
- [read] [Federal Reserve: About the Fed](https://www.federalreserve.gov/aboutthefed.htm). What a central bank actually does.
