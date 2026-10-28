# 08 · Financial Statements & Ratios

**Big idea:** the three statements describe a company's performance and health; ratios make companies comparable.

## The three statements
- **Income statement** — revenue, costs and profit over a period.
- **Balance sheet** — assets, liabilities and equity at a moment. `Assets = Liabilities + Equity`.
- **Cash flow statement** — cash from operations, investing and financing.

## Key ratios
| Group | Ratios | Code |
|---|---|---|
| Profitability | gross / operating / net margin, ROA, ROE | `statements.profitability_ratios` |
| Liquidity | current ratio, quick ratio | `statements.liquidity_ratios` |
| Leverage | debt-to-equity, debt-to-assets, interest coverage | `statements.leverage_ratios` |
| DuPont | ROE = margin × turnover × leverage | `statements.dupont` |

## Run it
```bash
python examples/08_financial_statements.py
```

## Exercises
1. Plug in numbers from a real company's annual report. How does it compare with a competitor?
2. Using DuPont, show how two firms can have the same ROE for very different reasons.
3. Add a `CashFlowStatement` dataclass and compute free cash flow.
