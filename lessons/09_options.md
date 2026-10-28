# 09 · Options (Intro to Derivatives)

**Big idea:** an option is a right, not an obligation. Its value comes from the chance the underlying moves in your favor before expiry.

## Key concepts
| Concept | Formula | Code |
|---|---|---|
| Call payoff | `max(S − K, 0)` | `options.call_payoff` |
| Put payoff | `max(K − S, 0)` | `options.put_payoff` |
| Black-Scholes call | `S N(d₁) − K e^(−rT) N(d₂)` | `options.black_scholes_call` |
| Black-Scholes put | `K e^(−rT) N(−d₂) − S N(−d₁)` | `options.black_scholes_put` |
| Put-call parity | `C − P = S − K e^(−rT)` | `options.put_call_parity_put` |
| Delta | `N(d₁)` | `options.call_delta` |

## Intuition
- More volatility → more valuable options (upside is unlimited, downside is capped at the premium).
- Delta is roughly the probability-weighted exposure to the stock; it is also the hedge ratio.

## Run it
```bash
python examples/09_options.py
```

## Exercises
1. Price a call with a Monte Carlo simulation and compare it with Black-Scholes.
2. Write an `implied_volatility` function that solves for vol given a market price (hint: reuse bisection from lesson 02).
