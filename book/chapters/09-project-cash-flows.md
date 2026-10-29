# Estimating Project Cash Flows

The NPV rule is only as good as the cash flows you feed it. In practice, the hard part of capital budgeting isn't discounting. It's working out **which cash flows to include**. This chapter teaches the principles analysts use to build a project's free cash flow forecast, and how to stress-test it.

> [!IMPORTANT]
> Value a project using its **incremental, after-tax free cash flows**: the difference between the firm's cash flows *with* the project and *without* it. Not accounting profit, and not the firm's total cash.

## What counts as an incremental cash flow?

| Include ✓ | Exclude ✗ |
|---|---|
| **Opportunity costs**: the building you'd otherwise rent out | **Sunk costs**: market research already paid for |
| **Side effects**: lost sales of your existing products (cannibalization) | **Allocated overhead** that doesn't change with the project |
| **Working capital** tied up in inventory and receivables | **Financing costs** (interest, dividends). The discount rate handles financing |
| **Taxes**, including the tax saved by depreciation | Accounting profit itself (we start from it, then convert to cash) |

> [!WARNING]
> **Don't subtract interest from project cash flows.** The cost of capital already reflects how the project is financed. Subtracting interest as well counts financing twice.

## From profit to free cash flow

Start from the project's operating profit (EBIT), tax it, add back depreciation (a non-cash expense), and subtract the cash the project needs for new equipment and working capital:

\[ FCF = \underbrace{EBIT\,(1 - t)}_{\text{after-tax operating profit}} + \text{Depreciation} - \text{CapEx} - \Delta NWC \]

Operating cash flow can also be written as after-tax profit before depreciation plus a **depreciation tax shield**:

\[ OCF = (\text{Revenue} - \text{Costs})(1 - t) + t \times \text{Depreciation} \]

```python run
from finance101 import project_cash_flows as pcf

revenue, costs, depreciation, tax = 1_000_000, 600_000, 150_000, 0.25
ocf = pcf.operating_cash_flow(revenue, costs, depreciation, tax)
print(f"Operating cash flow: ${ocf:,.0f}")
print(f"  = after-tax (revenue − costs): ${(revenue - costs) * (1 - tax):,.0f}")
print(f"  + depreciation tax shield    : ${tax * depreciation:,.0f}")
```

Depreciation itself isn't cash, but because it's tax-deductible it saves real cash: the tax rate times depreciation.

### Faster depreciation is worth more

Tax rules often allow **accelerated depreciation**. The total depreciation is the same, but more of it comes early, and early tax savings are worth more in present-value terms. Here's straight-line vs. the US MACRS 5-year schedule for a $1 million machine:

```python run
cost, tax_rate, r = 1_000_000, 0.25, 0.10
straight = [cost / 5] * 5 + [0]
macrs_5yr = [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576]    # IRS percentages (half-year convention)
macrs = [cost * p for p in macrs_5yr]

def pv_tax_shield(schedule):
    return sum(tax_rate * d / (1 + r) ** t for t, d in enumerate(schedule, start=1))

print(f"PV of tax shield, straight-line: ${pv_tax_shield(straight):,.0f}")
print(f"PV of tax shield, MACRS        : ${pv_tax_shield(macrs):,.0f}")
```

## Working capital

Launching a product means stocking inventory and waiting for customers to pay. That cash is tied up for the life of the project and comes back at the end. An **increase** in net working capital is a cash *outflow*; its recovery is an inflow.

## A complete project: the electric scooter line

A company is considering a new electric scooter line:

- Equipment costs **$2.4 million**, depreciated straight-line to zero over **4 years**; it can be sold for **$300,000** at the end.
- Expected sales: **8,000 scooters a year** at **$600** each; variable cost **$350** a unit; fixed costs **$500,000** a year.
- Net working capital of **$250,000** is needed at the start and recovered at the end.
- Tax rate **25%**; cost of capital **11%**.

```python run
from finance101 import capital_budgeting as cb

def scooter_project(units=8_000, price=600, unit_cost=350, fixed=500_000,
                    investment=2_400_000, salvage=300_000, nwc=250_000, tax=0.25, life=4):
    revenues = [units * price] * life
    costs = [units * unit_cost + fixed] * life
    return pcf.project_cash_flows(investment, revenues, costs, life, tax, salvage, nwc)

flows = scooter_project()
for year, cf in enumerate(flows):
    print(f"Year {year}: {cf:>12,.0f}")
print(f"\nNPV at 11%: ${cb.npv(0.11, flows):,.0f}   IRR: {cb.irr(flows):.1%}")
```

Look at year 4: it includes the regular operating cash flow, the recovered working capital, and the after-tax salvage value.

## Stress-testing the forecast

Every input above is a guess. Good analysts ask: **which assumptions matter most, and how wrong can they be before the project loses money?**

### Sensitivity analysis

Change one input at a time, holding everything else fixed:

```python run
base = cb.npv(0.11, scooter_project())
tests = {"units": (6_000, 10_000), "price": (540, 660), "unit_cost": (315, 385), "fixed": (400_000, 600_000)}

print(f"{'input':<10} {'low case':>12} {'high case':>12}")
for name, (low, high) in tests.items():
    npv_low = cb.npv(0.11, scooter_project(**{name: low}))
    npv_high = cb.npv(0.11, scooter_project(**{name: high}))
    print(f"{name:<10} {npv_low:>12,.0f} {npv_high:>12,.0f}")
print(f"{'base':<10} {base:>12,.0f}")
```

Price and volume dominate. A 10% price cut destroys about two-thirds of the NPV, while a 20% swing in fixed costs barely matters. That tells management where to focus research before deciding: pin down what customers will pay and how many they'll buy.

### Break-even analysis

How many scooters must we sell each year for NPV to be zero?

```python run
import matplotlib.pyplot as plt

units_range = list(range(4_000, 12_001, 250))
npvs = [cb.npv(0.11, scooter_project(units=u)) for u in units_range]

low, high = 1_000, 20_000                         # bisection on units
for _ in range(50):
    mid = (low + high) / 2
    low, high = (mid, high) if cb.npv(0.11, scooter_project(units=mid)) < 0 else (low, mid)
print(f"NPV break-even volume: {mid:,.0f} scooters per year")

plt.plot(units_range, [v / 1e6 for v in npvs])
plt.axhline(0, color="gray", linewidth=0.8)
plt.axvline(mid, linestyle="--", color="gray")
plt.title("Scooter project: NPV vs. annual unit sales")
plt.xlabel("Units sold per year"); plt.ylabel("NPV ($ millions)")
plt.grid(alpha=0.3)
plt.show()
```

### Scenario analysis

Inputs usually move together: a recession lowers both volume and price. A **scenario** changes several inputs at once:

```python run
scenarios = {
    "Pessimistic": dict(units=6_500, price=560, unit_cost=370),
    "Base case": dict(),
    "Optimistic": dict(units=9_500, price=630, unit_cost=340),
}
probabilities = {"Pessimistic": 0.25, "Base case": 0.50, "Optimistic": 0.25}

expected = 0
for name, inputs in scenarios.items():
    value = cb.npv(0.11, scooter_project(**inputs))
    expected += probabilities[name] * value
    print(f"{name:<12} NPV {value:>12,.0f}")
print(f"{'Expected':<12} NPV {expected:>12,.0f}")
```

> [!NOTE]
> Sensitivity and scenario analysis don't change the decision rule, but they show **how fragile** the NPV is. That helps managers decide whether to gather more information, run a smaller pilot, or build in options to expand or abandon later.

## Key takeaways

- Use **incremental, after-tax free cash flows**: include opportunity costs, side effects and working capital; exclude sunk costs and financing costs.
- \(FCF = EBIT(1-t) + \text{Depreciation} - \text{CapEx} - \Delta NWC\).
- Depreciation saves tax worth \(t \times D\) per year; faster depreciation is worth more.
- **Sensitivity**, **break-even** and **scenario** analysis reveal which assumptions drive the decision.

## Exercises

1. The firm already spent $150,000 on market research for the scooter. Should it be in the cash flows?
2. Using the scooter model, what is the NPV if the equipment costs $2.8 million instead?
3. Find the break-even **price** per scooter (hold all else at base).
4. The scooter line will cannibalize an existing bike line, reducing its after-tax cash flow by $120,000 a year for 4 years. Recompute NPV including this side effect.

<details>
<summary>Solutions</summary>

```python run
print("1. No: it is a sunk cost, spent whether or not the project goes ahead.")
print(f"2. NPV with $2.8M equipment: ${cb.npv(0.11, scooter_project(investment=2_800_000)):,.0f}")
low, high = 300, 900
for _ in range(60):
    mid = (low + high) / 2
    low, high = (mid, high) if cb.npv(0.11, scooter_project(price=mid)) < 0 else (low, mid)
print(f"3. Break-even price: ${mid:,.2f}")
with_side_effect = [cf - (120_000 if t > 0 else 0) for t, cf in enumerate(scooter_project())]
print(f"4. NPV including cannibalization: ${cb.npv(0.11, with_side_effect):,.0f}")
```

</details>

## Watch & read

- [watch] [Aswath Damodaran: Corporate Finance course (NYU, free lectures)](https://pages.stern.nyu.edu/~adamodar/). Under "Courses", the corporate finance lectures cover estimating incremental cash flows with real cases.
- [read] [Investopedia: Free Cash Flow](https://www.investopedia.com/terms/f/freecashflow.asp). Definitions and the different variants.
- [read] [OpenStax *Principles of Finance*, Chapter 16](https://openstax.org/details/books/principles-finance). Includes cash flow estimation and sensitivity analysis.
- [read] [IRS Publication 946: How to Depreciate Property](https://www.irs.gov/publications/p946). The official MACRS tables used above.
