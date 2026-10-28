# 04 · Bonds

**Big idea:** a bond's price is the present value of its coupons plus its face value. When yields rise, prices fall.

## Key concepts
| Concept | Meaning | Code |
|---|---|---|
| Price | PV of coupons + face at the bond's yield | `bonds.bond_price` |
| Yield to maturity | the single discount rate that equates PV to price | `bonds.yield_to_maturity` |
| Current yield | annual coupon / price | `bonds.current_yield` |
| Macaulay duration | weighted-average time to receive cash (years) | `bonds.macaulay_duration` |
| Modified duration | `%ΔP ≈ −ModDur × Δy` | `bonds.modified_duration` |
| Convexity | curvature correction to duration | `bonds.convexity` |

## Intuition
- Coupon > yield → bond trades at a **premium**; coupon < yield → **discount**; equal → **par**.
- Longer maturity and lower coupons mean higher duration, i.e. more interest-rate risk.
- A zero-coupon bond's duration equals its maturity.

## Run it
```bash
python examples/04_bonds.py
```

## Exercises
1. Use duration and convexity to estimate the price change of a 10-year 5% bond for a +200bp shock, then compare to full repricing.
2. Plot price vs. yield for a 2-year and a 30-year bond. Which curve is steeper? Which is more curved?
