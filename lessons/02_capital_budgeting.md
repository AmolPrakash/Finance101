# 02 · Capital Budgeting (NPV & IRR)

**Big idea:** a project is worth doing if the present value of what it returns exceeds what it costs.

## Key concepts
| Concept | Rule | Code |
|---|---|---|
| Net present value | `Σ CF_t / (1 + r)^t`; accept if NPV > 0 | `capital_budgeting.npv` |
| Internal rate of return | rate where NPV = 0; accept if IRR > required return | `capital_budgeting.irr` |
| Payback period | years to recover the investment (ignores time value) | `capital_budgeting.payback_period` |
| Discounted payback | payback using discounted cash flows | `capital_budgeting.discounted_payback_period` |
| Profitability index | PV(future CFs) / investment; accept if > 1 | `capital_budgeting.profitability_index` |

## Intuition
- **NPV is the gold standard**: it measures value created in today's dollars.
- IRR is convenient but can mislead with unconventional cash flows (multiple sign changes) or when ranking projects of different size.
- Payback is popular because it's simple, but it ignores everything after the payback date.

## Run it
```bash
python examples/02_capital_budgeting.py
```

## Exercises
1. In the example, at what discount rate do the two projects have equal NPV (the crossover rate)?
2. Build cash flows `[-100, 230, -132]`. How many IRRs does it have? Why is that a problem?
3. Why might a firm with limited capital prefer the profitability index to NPV?
