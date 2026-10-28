# 07 · Portfolios, Diversification & CAPM

**Big idea:** combining assets that don't move together lowers risk. Only risk that can't be diversified away (market risk, measured by beta) earns a reward.

## Key concepts
| Concept | Formula | Code |
|---|---|---|
| Portfolio return | `Σ wᵢ E[Rᵢ]` | `portfolio.portfolio_return` |
| Portfolio variance | `wᵀ Σ w` | `portfolio.portfolio_variance` |
| Two-asset volatility | depends on correlation ρ | `portfolio.two_asset_volatility` |
| Minimum-variance mix | lowest-risk two-asset weight | `portfolio.min_variance_weight` |
| Beta | `Cov(Rᵢ, Rm) / Var(Rm)` | `portfolio.beta` |
| CAPM | `E[R] = Rf + β (E[Rm] − Rf)` | `portfolio.capm_expected_return` |
| WACC | blended after-tax cost of capital | `portfolio.wacc` |

## Intuition
- Unless correlation is +1, a portfolio's risk is less than the weighted average of its parts.
- CAPM gives the **required return** used as the discount rate in lessons 02 and 05.
- WACC ties it together: it is the hurdle rate for a firm's projects.

## Run it
```bash
python examples/07_portfolio_and_capm.py
```

## Exercises
1. Trace the efficient frontier for two assets: loop weights 0→1 and print (volatility, return).
2. Estimate a stock's beta from monthly returns against an index.
