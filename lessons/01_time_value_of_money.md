# 01 · Time Value of Money

**Big idea:** a dollar today is worth more than a dollar later, because today's dollar can earn a return. Every valuation in finance is an application of this one idea.

## Key concepts
| Concept | Formula | Code |
|---|---|---|
| Future value | `FV = PV × (1 + r)^n` | `time_value.future_value` |
| Present value (discounting) | `PV = FV / (1 + r)^n` | `time_value.present_value` |
| Effective annual rate | `EAR = (1 + APR/m)^m − 1` | `time_value.effective_annual_rate` |
| Annuity PV | `PMT × [1 − (1 + r)^−n] / r` | `time_value.present_value_annuity` |
| Growing perpetuity | `PMT / (r − g)` | `time_value.present_value_perpetuity` |
| Real rate (Fisher) | `(1 + nominal) / (1 + inflation) − 1` | `time_value.real_rate` |

## Intuition
- **Compounding** earns interest on interest; its effect explodes with time.
- **Discounting** runs compounding backwards: it answers "what is a future amount worth now?"
- The **rate** is your opportunity cost — what you could earn elsewhere at similar risk.
- APR understates the true cost when compounding happens more than once a year.

## Run it
```bash
python examples/01_time_value_of_money.py
```

## Exercises
1. How much must you save monthly for 25 years at 6% to retire with $1,000,000?
2. Which is better: $50,000 today or $8,000 a year for 10 years, at 8%?
3. A bank quotes 5.9% compounded daily, another 6.0% compounded annually. Which pays more?
4. Your salary rose 4% while inflation was 6%. What happened to your real pay?
