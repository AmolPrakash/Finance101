# Capital Structure and Payout Policy

Should a company finance itself with debt or equity? Should it return cash to shareholders as dividends or buy back shares? These questions sound like they should have obvious answers. The surprising insight of modern finance is that in a frictionless world, **neither choice changes the value of the firm**. Real-world value comes from the *frictions*: taxes, bankruptcy costs, information and incentives.

> [!IMPORTANT]
> **Modigliani-Miller (MM):** with no taxes, transaction costs or bankruptcy costs, a firm's value depends only on its assets' cash flows, not on how those cash flows are split between debt and equity holders. Slicing a pizza differently doesn't make more pizza.

## MM Proposition I: capital structure is irrelevant (without taxes)

Imagine two firms with identical assets producing identical cash flows. One is all-equity; the other has borrowed. Their total values must be equal. Otherwise investors could create the same payoffs more cheaply with **homemade leverage**, borrowing on their own account.

```python run
# Same business, three possible states of the economy
ebit = {"recession": 400, "normal": 1_000, "boom": 1_600}

def payoffs(debt, rate=0.05):
    """Cash flow to all investors, and to equity holders, for each state (no taxes)."""
    interest = debt * rate
    return {s: {"to_equity": e - interest, "to_debt": interest, "total": e} for s, e in ebit.items()}

for debt in [0, 5_000]:
    print(f"Debt = {debt}:")
    for state, flows in payoffs(debt).items():
        print(f"  {state:<10} equity gets {flows['to_equity']:>6,.0f}   debt gets {flows['to_debt']:>4,.0f}   total {flows['total']:>6,.0f}")
```

The **total** cash flow to investors doesn't change with leverage. Only its split does. So the total value can't change either.

## MM Proposition II: leverage makes equity riskier

Debt doesn't lower the cost of capital, even though debt is "cheaper" than equity. Adding debt makes the remaining equity riskier, and shareholders demand more:

\[ r_E = r_U + \frac{D}{E}\,(r_U - r_D) \]

where \(r_U\) is the cost of capital of the unlevered firm.

```python run
from finance101 import capital_structure as cs
from finance101 import portfolio as pf

r_u, r_d = 0.10, 0.05
print(" D/V    D/E    r_E     WACC (no tax)")
for debt_share in [0.0, 0.2, 0.4, 0.6, 0.8]:
    d_e = debt_share / (1 - debt_share)
    r_e = cs.cost_of_equity_levered(r_u, r_d, d_e)
    wacc = pf.wacc(1 - debt_share, debt_share, r_e, r_d, tax_rate=0.0)
    print(f"{debt_share:>4.0%}  {d_e:>5.2f}  {r_e:>6.1%}  {wacc:>6.1%}")
```

The WACC stays at 10% at every leverage level. The benefit of cheap debt is exactly offset by the rising cost of equity.

## Adding corporate taxes: the interest tax shield

Interest is tax-deductible, so debt **saves taxes**. Each year, the government takes less, and investors as a group keep more. With permanent debt \(D\) and tax rate \(t\):

\[ V_L = V_U + t \times D \]

```python run
v_unlevered = 10_000
tax = 0.25
for debt in [0, 2_000, 4_000, 6_000]:
    print(f"Debt {debt:>5,}: firm value {cs.levered_value(v_unlevered, debt, tax):>7,.0f}  (tax shield worth {tax * debt:,.0f})")
```

Taken literally, this says firms should be financed almost entirely with debt. They aren't. Why not?

## The trade-off theory

Debt has costs too. As leverage rises, so does the probability of **financial distress**: lost customers and suppliers, fire sales, legal fees, and managers forced to pass up good projects. The **trade-off theory** says firms balance the tax benefit of debt against the expected costs of distress:

\[ V_L = V_U + PV(\text{tax shield}) - PV(\text{distress costs}) \]

```python run
import matplotlib.pyplot as plt

debt_levels = list(range(0, 9_001, 250))
tax_shield = [tax * d for d in debt_levels]
distress = [0.00004 * max(d - 2_000, 0) ** 2 for d in debt_levels]   # illustrative: rises fast at high debt
value = [v_unlevered + ts - dc for ts, dc in zip(tax_shield, distress)]

best = debt_levels[value.index(max(value))]
plt.plot(debt_levels, value, label="Levered firm value")
plt.plot(debt_levels, [v_unlevered + ts for ts in tax_shield], linestyle="--", label="MM with taxes (no distress costs)")
plt.axhline(v_unlevered, color="gray", linewidth=0.8, label="Unlevered value")
plt.axvline(best, color="gray", linestyle=":")
plt.title(f"Trade-off theory: optimal debt ≈ {best:,}")
plt.xlabel("Debt"); plt.ylabel("Firm value")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

This explains real patterns: firms with stable cash flows and tangible assets (utilities, real estate) borrow a lot; firms with risky cash flows and intangible assets (biotech, software) borrow little.

### The pecking order

Managers know more about their firm than outside investors do. Issuing new shares signals that management thinks they're overvalued, so stock prices typically fall on announcement. The **pecking order theory** predicts firms prefer **internal funds** first, then **debt**, and **new equity** only as a last resort.

## Levering and unlevering beta

Leverage changes equity risk, so a firm's equity beta depends on its capital structure. To compare business risk across firms, or to estimate a beta for a different capital structure, use the **Hamada** relation:

\[ \beta_L = \beta_U\left[1 + (1 - t)\frac{D}{E}\right] \]

```python run
# Comparable firm: equity beta 1.4 with D/E of 0.8. Our firm will have D/E of 0.3.
beta_u = cs.unlevered_beta(1.4, debt_to_equity=0.8, tax_rate=0.25)
beta_ours = cs.levered_beta(beta_u, debt_to_equity=0.3, tax_rate=0.25)
print(f"Asset (unlevered) beta: {beta_u:.2f}")
print(f"Our equity beta at D/E 0.3: {beta_ours:.2f}")
```

## Leverage and EPS

Debt **amplifies** earnings per share: higher EPS in good times and lower in bad times.

```python run
def eps_table(debt, shares, rate=0.06, tax=0.25):
    return {state: cs.earnings_per_share(e, debt * rate, tax, shares) for state, e in ebit.items()}

all_equity = eps_table(debt=0, shares=1_000)
levered = eps_table(debt=5_000, shares=500)       # borrow 5,000 and buy back half the shares at $10
for state in ebit:
    print(f"{state:<10} EPS all-equity {all_equity[state]:>5.2f}   EPS levered {levered[state]:>5.2f}")
```

Higher average EPS doesn't mean higher value: the levered EPS is also riskier, and MM says the two effects cancel (before taxes).

## Payout policy: dividends vs. buybacks

Firms return cash in two ways:

- **Dividends:** cash paid to every shareholder.
- **Share repurchases (buybacks):** the firm buys its own shares, so only shareholders who choose to sell receive cash.

In an MM world, payout policy is also irrelevant: a dividend lowers the share price by the amount paid, and a fair-priced buyback leaves the price unchanged. Either way, shareholders end up with the same total wealth.

```python run
equity_value, shares, cash_out = 10_000, 1_000, 1_000

# Dividend: price falls by the dividend per share
div_per_share = cash_out / shares
price_after_div = (equity_value - cash_out) / shares
print(f"Dividend : stock ${price_after_div:.2f} + cash ${div_per_share:.2f} = ${price_after_div + div_per_share:.2f} per original share")

# Buyback at the fair price
price_after, shares_after = cs.share_price_after_buyback(equity_value, shares, cash_out)
print(f"Buyback  : price stays ${price_after:.2f}, shares fall to {shares_after:,.0f}")
```

In reality, the choice matters because of:

- **Taxes:** buybacks let investors choose when to realize capital gains, often taxed more lightly than dividends.
- **Signaling:** dividend cuts are punished severely, so firms raise dividends only when confident about future earnings.
- **Flexibility:** buybacks can be scaled up or down quietly; dividends are "sticky".
- **Agency:** paying out excess cash stops managers from wasting it on poor investments.

## Key takeaways

- **MM I:** without frictions, capital structure doesn't change firm value. **MM II:** debt raises the cost of equity, leaving WACC unchanged.
- With taxes, debt adds a **tax shield** worth \(t \times D\) (for permanent debt).
- The **trade-off theory** balances tax shields against distress costs; the **pecking order** reflects information problems.
- Unlever and relever betas with \(\beta_L = \beta_U[1 + (1 - t)D/E]\).
- Payout policy is irrelevant in an MM world; taxes, signaling and agency make it matter in practice.

## Exercises

1. An unlevered firm is worth $50 million. It issues $20 million of permanent debt and uses it to buy back shares. With a 21% tax rate, what is the firm's new value under MM with taxes?
2. \(r_U\) = 11%, \(r_D\) = 6%, D/E = 1.5, tax rate 25%. What is the cost of equity?
3. In the EPS example, at what level of EBIT do the all-equity and levered structures produce the same EPS?

<details>
<summary>Solutions</summary>

```python run
print(f"1. ${cs.levered_value(50, 20, 0.21):.1f} million")
print(f"2. r_E = {cs.cost_of_equity_levered(0.11, 0.06, 1.5, 0.25):.2%}")
# EPS equal: (EBIT)(1-t)/1000 = (EBIT - 300)(1-t)/500  →  EBIT = 600
for e in [500, 600, 700]:
    print(f"3. EBIT {e}: all-equity {cs.earnings_per_share(e, 0, 0.25, 1000):.3f}, levered {cs.earnings_per_share(e, 300, 0.25, 500):.3f}")
```

</details>

## Watch & read

- [course] [MIT OCW 15.402 Finance Theory II](https://ocw.mit.edu/courses/15-402-finance-theory-ii-spring-2003/). Lecture notes on capital structure, payout policy and corporate financing decisions.
- [read] [Investopedia: Modigliani-Miller Theorem](https://www.investopedia.com/terms/m/modigliani-millertheorem.asp). A short summary of MM and its assumptions.
- [read] [The Nobel Prize: Franco Modigliani (1985)](https://www.nobelprize.org/prizes/economic-sciences/1985/summary/) and [Merton Miller (1990)](https://www.nobelprize.org/prizes/economic-sciences/1990/summary/). The laureates' lectures and background on the ideas in this chapter.
- [read] [OpenStax *Principles of Finance*, Chapter 17: How Firms Raise Capital](https://openstax.org/details/books/principles-finance). Equity and debt financing in practice.
- [watch] [Aswath Damodaran's corporate finance lectures](https://pages.stern.nyu.edu/~adamodar/). The "financing decision" and "dividend policy" sessions apply these ideas to real companies.
