# 05 · Stock Valuation

**Big idea:** a share is worth the present value of the cash it will deliver to its owners.

## Key concepts
| Concept | Formula | Code |
|---|---|---|
| Gordon growth model | `P₀ = D₁ / (r − g)` | `equity.gordon_growth_value` |
| Implied return | `r = D₁ / P₀ + g` | `equity.implied_required_return` |
| Two-stage DDM | explicit high growth, then a perpetuity | `equity.two_stage_ddm` |
| Discounted cash flow | PV(free cash flows) + PV(terminal value) | `equity.dcf_value` |
| P/E multiple | price / earnings per share | `equity.price_to_earnings` |

## Intuition
- Valuations are extremely sensitive to `r − g`; small changes in growth assumptions swing value wildly.
- In most DCFs, the terminal value is the majority of the answer — scrutinize it.
- A high P/E means the market expects high growth (or low risk).

## Run it
```bash
python examples/05_stock_valuation.py
```

## Exercises
1. In the DCF example, what share of total value comes from the terminal value?
2. Build a table of Gordon values for r in 7–11% and g in 1–5%. Where does the model break down?
