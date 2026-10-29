# How to Use This Book (and a Python Primer)

This is a finance textbook you can *run*. Each chapter explains an idea in plain language, shows the formula, and then hands you working Python code. You can change the code and run it right on the page. Python runs inside your browser, so there's nothing to install and nothing to pay for.

The book covers four courses, each building on the one before:

| Course | Focus | You will be able to… |
|---|---|---|
| **FIN 101** Foundations | Time value of money, interest, loans, financial statements, personal finance | Price any stream of cash flows, read an annual report, plan a retirement |
| **FIN 102** Corporate Finance | Capital budgeting, bonds, stocks, cost of capital, capital structure | Decide whether a project is worth funding and value a company |
| **FIN 201** Investments | Risk, return, portfolios, CAPM, factor models, yield curves, performance | Build and evaluate a diversified portfolio |
| **FIN 202** Derivatives & Risk | Forwards, futures, swaps, options, binomial trees, Black-Scholes, Monte Carlo, VaR | Price derivatives and measure a portfolio's risk |

> [!TIP]
> The fastest way to learn is to **predict before you run**. Before pressing Run, guess the answer. If you're surprised, that's where the learning happens.

## How the pages work

- **Code cells** like the one below are editable. Click into one, change something, and press **Shift+Enter** (or the ▶ Run button).
- The **first run** takes a few seconds while Python loads. After that, cells run instantly.
- Cells in a chapter **share variables**, like a Jupyter notebook. If a cell uses a variable from an earlier cell, run the earlier one first, or use **▶ Run all cells** at the top of the chapter.
- The **Scratchpad** (top-right button, or `Ctrl + .`) opens a Python editor next to the text. It shares variables with the chapter, so you can poke at results while you keep reading. Any cell's **Open in scratchpad** button copies its code there.
- The **Code Lab** lets you open and run *every* `.py` file in the repository: the `finance101` library, the example scripts and the full test suite.
- **Mark chapter complete** at the bottom of each chapter tracks your progress in this browser.

Try your first cell:

```python run
print("Hello, finance!")
2 + 2
```

The last line of a cell, if it is an expression, is shown automatically (that's why `4` appears). Anything you `print` appears too.

## The `finance101` library

Every formula in this book is implemented in a small Python package called `finance101`, which lives in this repository. Each function is a few lines long and names the formula it computes, so reading the code is part of learning the material.

```python run
from finance101 import time_value as tv

# What does $1,000 grow to in 10 years at 7% a year?
tv.future_value(1000, 0.07, 10)
```

You can read any function's documentation with `help`:

```python run
help(tv.future_value)
```

> [!NOTE]
> The library uses only Python's standard library (`math`, `statistics`, `random`), so nothing hides the math. Some chapters also use **NumPy** and **Matplotlib** for charts and bigger calculations; they load automatically the first time a cell imports them.

## A Python primer for finance

If you've never programmed, this section gives you everything you need for the rest of the book. If you already know Python, skim it.

### Numbers, variables and arithmetic

A **variable** is a name for a value. Finance uses decimals for rates: 5% is `0.05`.

```python run
principal = 10_000      # underscores make big numbers readable
rate = 0.05             # 5% per year
years = 3

balance = principal * (1 + rate) ** years   # ** means "to the power of"
balance
```

### Formatting money and percentages

**f-strings** (strings that start with `f`) insert values into text. The part after the colon controls the format: `,.2f` means "thousands separator, two decimals", and `.1%` means "as a percentage with one decimal".

```python run
print(f"Balance after {years} years: ${balance:,.2f}")
print(f"Total growth: {balance / principal - 1:.1%}")
```

### Lists and loops

A **list** holds several values in order. A **for loop** repeats a block of code once for each item. Indentation (four spaces) marks the block.

```python run
cash_flows = [-1000, 300, 400, 500]   # year 0 is today: a $1,000 investment

for year, cf in enumerate(cash_flows):
    print(f"Year {year}: {cf:>6}")

print("Sum of cash flows:", sum(cash_flows))
```

### Functions

A **function** packages a calculation so you can reuse it. `def` defines one; `return` sends back the answer.

```python run
def grow(amount, rate, years):
    """Return the value of `amount` after compounding for `years`."""
    return amount * (1 + rate) ** years

for r in [0.02, 0.05, 0.08]:
    print(f"At {r:.0%}: ${grow(1000, r, 30):>10,.2f}")
```

### Making decisions with `if`

```python run
def verdict(npv):
    if npv > 0:
        return "Accept: the project creates value"
    elif npv == 0:
        return "Indifferent"
    else:
        return "Reject: the project destroys value"

verdict(125.50)
```

### List comprehensions

A compact way to build a list from another list. Read it as "*this expression*, for each item in *that list*".

```python run
rates = [0.01 * i for i in range(1, 11)]          # 1%, 2%, ..., 10%
doubling = [round(72 / (r * 100), 1) for r in rates]
list(zip(rates, doubling))[:4]
```

### Dictionaries

A **dictionary** maps names to values, which is handy for labelled data like financial statements.

```python run
income_statement = {"revenue": 5000, "costs": 3200, "taxes": 450}
net_income = income_statement["revenue"] - income_statement["costs"] - income_statement["taxes"]
print(f"Net income: {net_income}  (margin {net_income / income_statement['revenue']:.1%})")
```

### Your first chart

Matplotlib draws charts. Charts appear under the cell when you run it. The first chart loads Matplotlib, which takes a few seconds.

```python run
import matplotlib.pyplot as plt

years = list(range(0, 41))
for r in [0.03, 0.06, 0.09]:
    plt.plot(years, [grow(10_000, r, t) for t in years], label=f"{r:.0%} per year")

plt.title("$10,000 growing at different rates")
plt.xlabel("Years")
plt.ylabel("Value ($)")
plt.legend()
plt.grid(alpha=0.3)
plt.show()
```

Look at the gap between the lines after 40 years. Small differences in rates create enormous differences in outcomes. That is the first big lesson of finance, and the subject of Chapter 2.

## When something goes wrong

Errors are normal and useful. Python tells you the line and the problem:

```python run error
# This cell has a deliberate mistake. Read the error, then fix it and re-run.
monthly_payment = 1200
print("Yearly payments:", monthly_payment * 12)
print("Monthly payment was", monthly_paymnt)
```

- **NameError**: a misspelled variable, or one defined in a cell you haven't run yet.
- **SyntaxError**: a missing bracket, quote or colon.
- **IndentationError**: inconsistent spaces at the start of a line.
- If a cell runs forever (an infinite loop), click **Restart Python** at the top of the chapter.

## Running the book on your own computer

Everything also works offline with regular Python:

```bash
git clone https://github.com/AmolPrakash/Finance101.git
cd Finance101
pip install -e ".[dev]"
python book/build.py --serve      # then open http://localhost:8000
pytest                            # run the test suite
```

## Exercises

1. Change the first `grow` example so it shows 10, 20 and 30 years at 7%.
2. Write a function `percent_change(old, new)` that returns the percentage change, and test it on a stock that went from $80 to $100.
3. Add a fourth line to the chart for 12% a year. How much bigger is it than the 9% line at year 40?

<details>
<summary>Solutions</summary>

```python run
for y in [10, 20, 30]:
    print(f"{y} years at 7%: ${grow(1000, 0.07, y):,.2f}")

def percent_change(old, new):
    return new / old - 1

print(f"{percent_change(80, 100):.1%}")
print(f"12% vs 9% after 40 years: {grow(10_000, 0.12, 40) / grow(10_000, 0.09, 40):.1f}x bigger")
```

</details>

## Watch & read

- [course] [Python's official tutorial](https://docs.python.org/3/tutorial/). The best free introduction to the language; sections 3–5 cover everything used here.
- [course] [QuantEcon: Python Programming for Economics and Finance](https://python.quantecon.org/). Free online lectures that teach Python through finance and economics problems.
- [read] [OpenStax: *Principles of Finance*](https://openstax.org/details/books/principles-finance). A free, peer-reviewed textbook to use alongside this book.
- [watch] [Khan Academy: Finance and capital markets](https://www.khanacademy.org/economics-finance-domain/core-finance). Short video explanations of nearly every topic in FIN 101 and 102.
