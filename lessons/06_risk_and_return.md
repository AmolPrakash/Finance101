# 06 · Risk & Return

**Big idea:** returns tell you what you earned; volatility tells you how bumpy the ride was. Higher expected return comes with higher risk.

## Key concepts
| Concept | Meaning | Code |
|---|---|---|
| Simple return | `P_t / P_{t−1} − 1` | `risk_return.simple_returns` |
| Log return | `ln(P_t / P_{t−1})`, additive over time | `risk_return.log_returns` |
| Annualized return (CAGR) | geometric average per year | `risk_return.annualized_return` |
| Volatility | standard deviation × √(periods per year) | `risk_return.volatility` |
| Sharpe ratio | excess return / volatility | `risk_return.sharpe_ratio` |
| Max drawdown | worst peak-to-trough fall | `risk_return.max_drawdown` |
| Value at Risk | loss not exceeded at a given confidence | `risk_return.historical_var` |

## Intuition
- +50% then −50% leaves you at −25%: arithmetic averages overstate compounded growth.
- Volatility scales with √time, not time.
- Drawdown captures the pain investors actually feel; volatility treats ups and downs alike.

## Run it
```bash
python examples/06_risk_and_return.py
```

## Exercises
1. Re-run the simulation with daily volatility of 2%. How do Sharpe and drawdown change?
2. Download real prices (e.g. a CSV from your broker) and run the same metrics.
