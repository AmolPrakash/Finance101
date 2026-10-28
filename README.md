# Finance101

Learning the fundamentals of finance by building them in Python.

Each topic is broken into four parts:

| Part | Where | Purpose |
|---|---|---|
| **Lesson** | `lessons/NN_topic.md` | Concepts, formulas, intuition, exercises |
| **Code** | `finance101/<module>.py` | Plain-Python implementation of every formula |
| **Example** | `examples/NN_topic.py` | Runnable script showing the ideas with real numbers |
| **Tests** | `tests/test_<module>.py` | Checks against textbook values — and documents behavior |

The library uses only the Python standard library, so nothing hides the math.

## Learning path

| # | Topic | Lesson | Module | Builds on |
|---|---|---|---|---|
| 01 | Time value of money | [lesson](lessons/01_time_value_of_money.md) | `time_value` | — |
| 02 | Capital budgeting (NPV, IRR) | [lesson](lessons/02_capital_budgeting.md) | `capital_budgeting` | 01 |
| 03 | Loans & amortization | [lesson](lessons/03_loans_and_amortization.md) | `loans` | 01 |
| 04 | Bonds | [lesson](lessons/04_bonds.md) | `bonds` | 01 |
| 05 | Stock valuation | [lesson](lessons/05_stock_valuation.md) | `equity` | 01, 02 |
| 06 | Risk & return | [lesson](lessons/06_risk_and_return.md) | `risk_return` | — |
| 07 | Portfolios, diversification & CAPM | [lesson](lessons/07_portfolio_and_capm.md) | `portfolio` | 06 |
| 08 | Financial statements & ratios | [lesson](lessons/08_financial_statements.md) | `statements` | — |
| 09 | Options | [lesson](lessons/09_options.md) | `options` | 01, 06 |

```
Finance101/
├── finance101/          # the library: one module per topic
├── lessons/             # notes: concepts, formulas, exercises
├── examples/            # runnable demos, one per lesson
└── tests/               # pytest suite with known-answer checks
```

## Getting started

Requires Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate
```

```bash
pip install -e ".[dev]"
```

Run an example:

```bash
python examples/01_time_value_of_money.py
```

Run the tests:

```bash
pytest
```

## How to study

1. Read the lesson.
2. Read the matching module — every function is a few lines and names its formula.
3. Run the example, then change the inputs and predict the output before you run it again.
4. Do the exercises; add a test for each new function you write.

## Where to go next

- Use `pandas` to load real price data and apply lessons 06–07.
- Plot NPV profiles, yield curves and efficient frontiers with `matplotlib`.
- Extend lesson 09 with implied volatility, the Greeks, and binomial trees.
