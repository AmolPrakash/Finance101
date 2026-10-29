"""Chapter 14: Measuring return and risk on a price series."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without installing

import random

from finance101 import risk_return as rr

random.seed(42)
prices = [100.0]
for _ in range(252 * 3):  # three years of simulated trading days
    prices.append(prices[-1] * (1 + random.gauss(0.0004, 0.012)))

returns = rr.simple_returns(prices)
print(f"Start {prices[0]:.2f} -> end {prices[-1]:.2f}")
print(f"Cumulative return:   {rr.cumulative_return(returns):.2%}")
print(f"Annualized return:   {rr.annualized_return(returns, 252):.2%}")
print(f"Annualized vol:      {rr.volatility(returns, 252):.2%}")
print(f"Sharpe (rf=4%):      {rr.sharpe_ratio(returns, 0.04, 252):.2f}")
print(f"Max drawdown:        {rr.max_drawdown(prices):.2%}")
print(f"1-day 95% VaR:       {rr.historical_var(returns, 0.95):.2%}")
