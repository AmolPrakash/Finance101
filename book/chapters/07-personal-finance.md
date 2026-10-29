# Personal Finance: Saving, Debt and Retirement

Everything you've learned so far applies directly to your own life. Should you pay off debt or invest? How much must you save for retirement? How much do fund fees really cost? These are time-value-of-money problems, and you can now solve them yourself.

> [!NOTE]
> This chapter teaches the math behind common personal-finance decisions. It is education, not individual financial advice. Your taxes, goals and circumstances matter.

> [!IMPORTANT]
> The three most powerful levers in personal finance are: **start early** (compounding needs time), **avoid high-interest debt** (it compounds against you), and **keep costs low** (fees compound too).

## Budgeting and the emergency fund

A popular starting rule is **50/30/20**: about 50% of take-home pay for needs, 30% for wants and 20% for saving and paying off debt. Before investing, most planners suggest an **emergency fund** of 3–6 months of essential expenses in a safe, accessible account.

```python run
take_home = 4_200          # monthly, after tax
budget = {"needs": 0.50, "wants": 0.30, "savings & debt": 0.20}
for item, share in budget.items():
    print(f"{item:<15} ${take_home * share:>7,.0f}")

essential_monthly = 2_300
print(f"\nEmergency fund target: ${3 * essential_monthly:,.0f} to ${6 * essential_monthly:,.0f}")
```

## Start early: the cost of waiting

Two savers each invest $400 a month at a 7% annual return until age 65. One starts at 25, the other at 35.

```python run
from finance101 import time_value as tv

monthly_rate = (1.07) ** (1 / 12) - 1
for start_age in [25, 35, 45]:
    months = (65 - start_age) * 12
    balance = tv.future_value_annuity(400, monthly_rate, months)
    contributed = 400 * months
    print(f"Start at {start_age}: contributed ${contributed:>8,.0f} → ${balance:>10,.0f} at 65")
```

Starting ten years earlier roughly doubles the outcome, even though you contribute only a third more money. Most of the final balance is growth, not contributions.

## Debt: avalanche vs. snowball

If you have several debts, which do you pay first with your extra money?

- **Avalanche:** highest interest rate first. Mathematically optimal.
- **Snowball:** smallest balance first. Quick wins can help motivation.

Let's simulate both:

```python run
def payoff(debts, monthly_budget, order):
    """Simulate paying debts with a fixed monthly budget. Returns (months, total interest)."""
    debts = [dict(d) for d in debts]
    month, interest_paid = 0, 0.0
    while any(d["balance"] > 0.01 for d in debts):
        month += 1
        for d in debts:                                   # interest accrues
            interest = d["balance"] * d["apr"] / 12
            d["balance"] += interest
            interest_paid += interest
        budget = monthly_budget
        for d in debts:                                   # minimum payments first
            pay = min(d["minimum"], d["balance"], budget)
            d["balance"] -= pay
            budget -= pay
        for d in sorted(debts, key=order):                # extra goes to the target debt
            pay = min(d["balance"], budget)
            d["balance"] -= pay
            budget -= pay
    return month, interest_paid

debts = [
    {"name": "credit card", "balance": 6_000, "apr": 0.24, "minimum": 150},
    {"name": "car loan", "balance": 12_000, "apr": 0.07, "minimum": 250},
    {"name": "medical bill", "balance": 1_500, "apr": 0.00, "minimum": 50},
    {"name": "store card", "balance": 2_000, "apr": 0.29, "minimum": 60},
]
budget = 1_000
for label, order in [("Avalanche (highest rate)", lambda d: -d["apr"]),
                     ("Snowball (smallest balance)", lambda d: d["balance"])]:
    months, interest = payoff(debts, budget, order)
    print(f"{label:<28} debt-free in {months} months, interest paid ${interest:,.0f}")
```

> [!TIP]
> Paying off a 24% credit card is a **guaranteed, tax-free 24% return**. No investment reliably beats that. Change the budget to $700 or $1,500 and see how the cost changes.

## Fees compound too

A 1% annual fee sounds small. Over decades, it isn't:

```python run
import matplotlib.pyplot as plt

years = list(range(0, 41))
gross = 0.07
for fee in [0.0005, 0.005, 0.01, 0.02]:
    plt.plot(years, [100_000 * (1 + gross - fee) ** t for t in years], label=f"{fee:.2%} fee")
plt.title("$100,000 invested at 7% before fees")
plt.xlabel("Years"); plt.ylabel("Value ($)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()

low, high = 100_000 * (1.07 - 0.0005) ** 40, 100_000 * (1.07 - 0.01) ** 40
print(f"After 40 years: 0.05% fee → ${low:,.0f}; 1% fee → ${high:,.0f}")
print(f"The 1% fee consumes {1 - high / low:.0%} of the ending wealth.")
```

This is why low-cost index funds became so popular.

## How much do you need to retire?

Retirement planning is two annuity problems back to back:

1. **Decumulation:** how big a nest egg can pay the income you want for your retirement years?
2. **Accumulation:** how much must you save each month to build it?

```python run
desired_income = 60_000        # per year, in today's dollars
years_in_retirement = 30
real_return = 0.03             # return after inflation, so we can work in today's dollars
working_years = 35

# 1. Nest egg needed at retirement (payments at the start of each year)
nest_egg = tv.present_value_annuity(desired_income, real_return, years_in_retirement, due=True)
print(f"Nest egg needed (today's dollars): ${nest_egg:,.0f}")

# 2. Required annual saving to get there
saving = tv.annuity_payment_for_goal(nest_egg, real_return, working_years)
print(f"Required saving: ${saving:,.0f} per year (${saving / 12:,.0f} per month)")

# The "4% rule" of thumb: withdraw 4% in year one, then adjust for inflation
print(f"Rule-of-thumb nest egg (income / 4%): ${desired_income / 0.04:,.0f}")
```

> [!NOTE]
> Working in **real** (inflation-adjusted) dollars with a **real** return keeps the problem simple: every number is in today's purchasing power. Mixing a nominal return with real income targets is a classic mistake.

### Employer match: an instant return

If your employer matches 50% of your contributions up to 6% of salary, every matched dollar earns an immediate 50% return before any market growth. It's almost always worth capturing the full match.

## Uncertainty: a range, not a number

Markets don't deliver a smooth 7% a year. Simulating thousands of possible return paths gives a **range** of outcomes. (Chapter 23 explains Monte Carlo simulation in depth.)

```python run
import statistics
from finance101.simulation import retirement_simulation

results = retirement_simulation(start_balance=0, annual_contribution=12_000, years=35,
                                mean_return=0.07, vol=0.15, simulations=3_000, seed=42)
results.sort()
pct = lambda p: results[int(p / 100 * (len(results) - 1))]
print(f"10th percentile: ${pct(10):>12,.0f}")
print(f"Median         : ${statistics.median(results):>12,.0f}")
print(f"90th percentile: ${pct(90):>12,.0f}")
print(f"Deterministic 7% answer: ${tv.future_value_annuity(12_000, 0.07, 35):,.0f}")

plt.hist([r / 1e6 for r in results], bins=60, color="#2f7d6b")
plt.title("Ending balance after 35 years ($ millions, nominal)")
plt.xlabel("$ millions"); plt.ylabel("Number of simulations")
plt.show()
```

The median is below the "7% every year" answer, because volatility drags down compound growth (Chapter 14). Plans should be robust to the bad scenarios, not just the average.

## Key takeaways

- Build an emergency fund first, and pay off high-interest debt before investing.
- **Time** is the biggest driver of wealth: starting ten years earlier can double the outcome.
- **Fees** and **interest** compound just like returns.
- Retirement planning = PV of retirement income (the nest egg), then the saving needed to reach it.
- Work in real dollars with real returns, and plan for a range of outcomes.

## Exercises

1. How much would the age-25 saver have at 65 if they invested $600 a month instead?
2. In the debt example, what happens to total interest if you only pay the minimums? (Hint: set the budget to the sum of minimums.)
3. Redo the retirement calculation with a 25-year retirement and a 4% real return. How much does the required saving fall?

<details>
<summary>Solutions</summary>

```python run
print(f"1. ${tv.future_value_annuity(600, monthly_rate, 480):,.0f}")
minimums = sum(d["minimum"] for d in debts)
months, interest = payoff(debts, minimums, lambda d: -d["apr"])
print(f"2. Minimums only (${minimums}/month): {months} months, interest ${interest:,.0f}")
egg = tv.present_value_annuity(60_000, 0.04, 25, due=True)
print(f"3. Nest egg ${egg:,.0f}; saving ${tv.annuity_payment_for_goal(egg, 0.04, 35):,.0f}/year")
```

</details>

## Watch & read

- [watch] [Khan Academy: Personal finance](https://www.khanacademy.org/college-careers-more/personal-finance). Free course covering budgeting, saving, credit, taxes, insurance and retirement.
- [course] [Coursera: Finance for Everyone: Smart Tools for Decision-Making (University of Michigan)](https://www.coursera.org/learn/finance-for-everyone). Time-value tools applied to everyday decisions; free to audit.
- [read] [Bogleheads wiki](https://www.bogleheads.org/wiki/Main_Page). A non-commercial, community-written guide to low-cost investing and retirement planning.
- [read] [Investor.gov: Introduction to investing](https://www.investor.gov/introduction-investing). The SEC's free, unbiased investor education.
- [tool] [Consumer Financial Protection Bureau](https://www.consumerfinance.gov/). Tools and guides for loans, credit cards and debt.
