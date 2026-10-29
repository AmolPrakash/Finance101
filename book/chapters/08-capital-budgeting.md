# Capital Budgeting: NPV, IRR and Friends

A company's most important decisions are about **what to invest in**: a new factory, a product launch, an acquisition, a software system. These decisions commit large sums for years. **Capital budgeting** is the toolkit for deciding which investments create value.

> [!IMPORTANT]
> **The NPV rule:** invest in a project if the present value of its future cash flows exceeds its cost, that is, if its **net present value is positive**. A positive NPV means the project earns more than investors could earn elsewhere at the same risk, so it makes the firm's owners richer by exactly that amount, today.

## Net present value

\[ NPV = \sum_{t=0}^{n} \frac{CF_t}{(1 + r)^t} = CF_0 + \frac{CF_1}{1 + r} + \frac{CF_2}{(1 + r)^2} + \cdots \]

where \(CF_0\) is usually negative (the investment) and \(r\) is the project's **cost of capital**: the return investors could earn on investments of similar risk (Chapter 12).

```python run
from finance101 import capital_budgeting as cb

# A food truck: costs $80k, then generates cash for 5 years
truck = [-80_000, 22_000, 25_000, 25_000, 24_000, 20_000]
rate = 0.10

print(f"NPV at {rate:.0%}: ${cb.npv(rate, truck):,.0f}")
```

The NPV is positive, so the food truck is worth more than it costs. Investors should pay about $8,000 more for a firm that owns this project than for one that doesn't.

### The NPV profile

NPV falls as the discount rate rises, because future cash flows are worth less. Plotting NPV against the rate gives the **NPV profile**:

```python run
import matplotlib.pyplot as plt

rates = [i / 1000 for i in range(0, 301, 5)]
plt.plot([r * 100 for r in rates], [cb.npv(r, truck) for r in rates])
plt.axhline(0, color="gray", linewidth=0.8)
irr = cb.irr(truck)
plt.scatter([irr * 100], [0], zorder=3)
plt.annotate(f"IRR = {irr:.1%}", (irr * 100, 0), xytext=(10, 20), textcoords="offset points")
plt.title("NPV profile of the food truck")
plt.xlabel("Discount rate (%)"); plt.ylabel("NPV ($)")
plt.grid(alpha=0.3)
plt.show()
```

## Internal rate of return

The **internal rate of return (IRR)** is the discount rate at which NPV equals zero: where the NPV profile crosses the axis. It's the project's own rate of return.

**IRR rule:** accept the project if IRR > cost of capital.

```python run
print(f"IRR: {cb.irr(truck):.2%}  vs cost of capital {rate:.0%} → {'accept' if cb.irr(truck) > rate else 'reject'}")
```

There's no formula for IRR. It must be found numerically. The library uses **bisection**: start with a rate that's too low and one that's too high, and keep halving the interval:

```python run
def irr_by_bisection(cash_flows, low=0.0, high=1.0, steps=30):
    for step in range(steps):
        mid = (low + high) / 2
        if cb.npv(mid, cash_flows) > 0:
            low = mid        # NPV still positive → the IRR is higher
        else:
            high = mid
        if step < 6 or step == steps - 1:
            print(f"step {step:>2}: IRR between {low:.4%} and {high:.4%}")
    return (low + high) / 2

irr_by_bisection(truck)
```

### When IRR misleads

IRR is intuitive, and executives love it, but it has three well-known problems.

**1. Multiple IRRs.** If cash flows change sign more than once (common in mining, where you pay a large cleanup cost at the end), there can be several IRRs, or none. Worse, the IRR rule can give the wrong answer: at a 10% cost of capital, this mine has a negative NPV, even though both of its IRRs are above 10%.

```python run
mine = [-1_000, 5_250, -5_000]    # invest, extract, pay for cleanup
for r in [0.10, 0.25, 0.50, 1.00, 2.00, 3.00, 4.00]:
    print(f"rate {r:>5.0%}: NPV {cb.npv(r, mine):>8.1f}")
print("NPV is zero at both 25% and 300%. Which one is 'the' return?")
```

**2. Scale.** IRR ignores size. Would you rather earn 50% on $10 or 20% on $10,000?

**3. Timing (mutually exclusive projects).** When you can only choose one project, IRR and NPV can rank them differently:

```python run
quick = [-10_000, 8_000, 4_000, 500]
slow = [-10_000, 1_000, 2_000, 11_500]
for name, cf in [("Quick payoff", quick), ("Slow payoff", slow)]:
    print(f"{name:<13} IRR {cb.irr(cf):6.2%}   NPV@8% {cb.npv(0.08, cf):>8,.0f}   NPV@15% {cb.npv(0.15, cf):>8,.0f}")

# Find the crossover rate where both projects have the same NPV
diff = [a - b for a, b in zip(quick, slow)]
print(f"\nCrossover rate: {cb.irr(diff):.2%}")
```

Below the crossover rate, the slow project has the higher NPV even though its IRR is lower. **When NPV and IRR disagree, follow NPV.** It measures the dollars of value created.

> [!TIP]
> Plot both NPV profiles in the scratchpad (copy the NPV profile code and add a second line). You'll see them cross at the crossover rate.

### Modified IRR

**MIRR** fixes the multiple-IRR problem by assuming interim cash flows are reinvested at the cost of capital:

```python run
def mirr(cash_flows, finance_rate, reinvest_rate):
    n = len(cash_flows) - 1
    fv_positive = sum(cf * (1 + reinvest_rate) ** (n - t) for t, cf in enumerate(cash_flows) if cf > 0)
    pv_negative = sum(cf / (1 + finance_rate) ** t for t, cf in enumerate(cash_flows) if cf < 0)
    return (fv_positive / -pv_negative) ** (1 / n) - 1

print(f"Mine MIRR at 10%: {mirr(mine, 0.10, 0.10):.2%}")
print(f"Truck MIRR at 10%: {mirr(truck, 0.10, 0.10):.2%}  (IRR was {cb.irr(truck):.2%})")
```

## Payback period

The **payback period** is how long it takes to recover the initial investment. It's simple and popular for small decisions, but it ignores the time value of money and *everything* after the cutoff. The **discounted payback** fixes the first problem but not the second.

```python run
print(f"Payback           : {cb.payback_period(truck):.2f} years")
print(f"Discounted payback: {cb.discounted_payback_period(rate, truck):.2f} years")

# Payback ignores everything after the cutoff:
lottery = [-1_000, 0, 0, 0, 50_000]
print(f"\nA project paying $50k in year 4 has payback {cb.payback_period(lottery):.2f} years "
      f"and would be rejected by a 3-year rule, despite NPV ${cb.npv(rate, lottery):,.0f}")
```

## Profitability index and capital rationing

The **profitability index (PI)** is value per dollar invested:

\[ PI = \frac{PV(\text{future cash flows})}{\text{Initial investment}} \]

It shines when capital is limited. With a fixed budget, you want the **combination** of projects with the highest total NPV:

```python run
from itertools import combinations

projects = {
    "A": [-40_000, 15_000, 15_000, 15_000, 15_000],
    "B": [-25_000, 9_000, 9_000, 9_000, 9_000],
    "C": [-30_000, 0, 10_000, 20_000, 25_000],
    "D": [-20_000, 8_000, 8_000, 8_000, 3_000],
}
budget = 75_000

for name, cf in projects.items():
    print(f"{name}: cost {-cf[0]:>6,}  NPV {cb.npv(rate, cf):>7,.0f}  PI {cb.profitability_index(rate, cf):.3f}")

best = max(
    (combo for k in range(1, len(projects) + 1) for combo in combinations(projects, k)
     if sum(-projects[p][0] for p in combo) <= budget),
    key=lambda combo: sum(cb.npv(rate, projects[p]) for p in combo),
)
print(f"\nBest set within ${budget:,}: {best}, total NPV ${sum(cb.npv(rate, projects[p]) for p in best):,.0f}")
```

## Projects with different lives

Comparing a machine that lasts 3 years with one that lasts 6 isn't fair: the short one has to be replaced. Convert each NPV to an **equivalent annual annuity (EAA)**, the level annual amount with the same NPV:

```python run
from finance101.project_cash_flows import equivalent_annual_annuity

cheap = [-50_000] + [22_000] * 3     # lasts 3 years
durable = [-90_000] + [22_000] * 6   # lasts 6 years
for name, cf in [("Cheap (3y)", cheap), ("Durable (6y)", durable)]:
    value = cb.npv(rate, cf)
    print(f"{name:<13} NPV {value:>8,.0f}   EAA {equivalent_annual_annuity(value, rate, len(cf) - 1):>7,.0f} per year")
```

The durable machine has the higher NPV, but the cheap one creates more value **per year**, and it can be replaced every three years.

## Key takeaways

- **NPV** is the gold standard: it measures the value a project adds, in today's dollars.
- **IRR** is the rate where NPV = 0. It's intuitive but can mislead with non-standard cash flows, different scales or different timing.
- **Payback** ignores the time value of money and later cash flows. Use it only as a rough screen.
- Under **capital rationing**, pick the combination with the highest total NPV; PI helps rank.
- Compare projects with **unequal lives** using the equivalent annual annuity.

## Exercises

1. At what cost of capital would the food truck have a zero NPV?
2. A project costs $500,000 and returns $140,000 a year for 5 years. At 12%, compute NPV, IRR, payback and PI. Accept or reject?
3. Plot the NPV profile of the mine for rates from 0% to 500%. Between which rates is NPV positive?

<details>
<summary>Solutions</summary>

```python run
print(f"1. Break-even cost of capital = IRR = {cb.irr(truck):.2%}")
p = [-500_000] + [140_000] * 5
print(f"2. NPV {cb.npv(0.12, p):,.0f}, IRR {cb.irr(p):.2%}, payback {cb.payback_period(p):.2f}y, PI {cb.profitability_index(0.12, p):.3f} → accept")
rs = [i / 100 for i in range(0, 501, 5)]
plt.plot(rs, [cb.npv(r, mine) for r in rs]); plt.axhline(0, color="gray")
plt.title("Mine: NPV profile"); plt.xlabel("rate"); plt.show()
print("3. NPV is positive between 25% and 300%. At a 10% cost of capital the mine destroys value, even though both IRRs exceed 10%.")
```

</details>

## Watch & read

- [watch] [MIT 15.401 Finance Theory I](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/). The "Capital Budgeting" lectures cover NPV, IRR and their pitfalls.
- [course] [Coursera: Introduction to Corporate Finance (Wharton)](https://www.coursera.org/learn/wharton-finance). Free to audit; the decision-making weeks are on exactly this material.
- [read] [OpenStax *Principles of Finance*, Chapter 16: How Companies Think about Investing](https://openstax.org/details/books/principles-finance). Capital budgeting methods with problems.
- [read] [Investopedia: Net Present Value](https://www.investopedia.com/terms/n/npv.asp) and [Internal Rate of Return](https://www.investopedia.com/terms/i/irr.asp). Quick references.
