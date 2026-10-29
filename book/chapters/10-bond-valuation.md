# Bond Valuation

A **bond** is a loan you can trade. The issuer (a government or company) borrows money and promises fixed payments: periodic **coupons** plus the **face value** at maturity. The global bond market is larger than the stock market, and bond yields set the "price of money" for the whole economy.

> [!IMPORTANT]
> A bond's price is the present value of its promised cash flows, discounted at the market's required yield. When market yields **rise**, bond prices **fall**, and long-term bonds fall the most.

## The vocabulary

| Term | Meaning |
|---|---|
| **Face (par) value** | Amount repaid at maturity, typically $1,000 |
| **Coupon rate** | Annual interest as a % of face; a 5% coupon pays $50 a year on $1,000 |
| **Maturity** | When the face value is repaid |
| **Yield to maturity (YTM)** | The discount rate that equates the bond's price to its cash flows: the return if you buy now and hold to maturity |
| **Current yield** | Annual coupon ÷ price |
| **Credit rating** | Agency assessment of default risk (AAA … BBB = investment grade; BB and below = "high yield" or "junk") |

## Pricing a bond

For a bond paying \(C\) per period for \(n\) periods, with face value \(F\) and yield per period \(y\):

\[ P = \sum_{t=1}^{n} \frac{C}{(1 + y)^t} + \frac{F}{(1 + y)^n} = C \times \frac{1 - (1+y)^{-n}}{y} + \frac{F}{(1 + y)^n} \]

It's an annuity (the coupons) plus a lump sum (the face value). Most US bonds pay coupons **semi-annually**, so we use half the annual coupon and half the annual yield per period.

```python run
from finance101 import bonds

face, coupon_rate, years = 1_000, 0.05, 10
for ytm in [0.03, 0.04, 0.05, 0.06, 0.07]:
    price = bonds.bond_price(face, coupon_rate, ytm, years)
    label = "premium" if price > face + 0.01 else "discount" if price < face - 0.01 else "par"
    print(f"YTM {ytm:.0%}: price ${price:>9,.2f}  ({label})")
```

- If the coupon rate **equals** the market yield, the bond sells at **par**.
- If the coupon rate is **above** the yield, investors pay a **premium**.
- If it's **below**, the bond sells at a **discount**, and the price gain to maturity makes up the shortfall.

### The price-yield curve

```python run
import matplotlib.pyplot as plt

yields = [i / 1000 for i in range(10, 121, 2)]
for maturity in [2, 10, 30]:
    plt.plot([y * 100 for y in yields], [bonds.bond_price(1000, 0.05, y, maturity) for y in yields], label=f"{maturity}-year")
plt.axvline(5, color="gray", linestyle=":", linewidth=1)
plt.title("Price vs. yield for 5% coupon bonds")
plt.xlabel("Yield to maturity (%)"); plt.ylabel("Price ($)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

Two lessons from this chart:

1. The curve slopes **down**: higher yields mean lower prices.
2. **Longer** bonds have steeper curves: they're far more sensitive to rate changes. That's **interest-rate risk**, measured by *duration* in Chapter 17.

> [!NOTE]
> In 2022, as inflation surged, long-term Treasury yields rose by more than 2 percentage points. Long-dated government bonds, considered "safe", lost over 25% of their value in a year. Safe from default is not the same as safe from price changes.

## Yield to maturity

Usually you observe the **price** and want the **yield**. Like IRR, YTM has no closed-form solution; we solve numerically:

```python run
price = 925.00
ytm = bonds.yield_to_maturity(price, face, 0.05, 10)
print(f"A 10-year 5% bond priced at ${price}: YTM = {ytm:.3%}")
print(f"Current yield: {bonds.current_yield(price, face, 0.05):.3%}")
print(f"Check: price at that YTM = ${bonds.bond_price(face, 0.05, ytm, 10):,.2f}")
```

YTM is the bond's IRR. It assumes you hold to maturity, receive every payment, and can reinvest coupons at the same yield.

## Zero-coupon bonds

A **zero-coupon bond** pays nothing until maturity, so it's priced as a single lump sum:

\[ P = \frac{F}{(1 + y)^n} \]

```python run
for years in [1, 5, 10, 30]:
    print(f"{years:>2}-year zero at 4.5% (annual compounding): ${bonds.bond_price(1000, 0.0, 0.045, years, frequency=1):,.2f}")
```

US Treasury STRIPS are zero-coupon bonds, and zeros are the building blocks of the yield curve (Chapter 17).

## Pull to par

As a bond approaches maturity, its price converges to face value, whatever the yield, because there's less and less time for the coupon difference to matter:

```python run
remaining = [10 - 0.5 * i for i in range(20)]
for coupon, label in [(0.07, "7% coupon (premium)"), (0.05, "5% coupon (par)"), (0.03, "3% coupon (discount)")]:
    plt.plot(remaining, [bonds.bond_price(1000, coupon, 0.05, t) for t in remaining], label=label)
plt.gca().invert_xaxis()
plt.title("Pull to par at a constant 5% yield")
plt.xlabel("Years to maturity"); plt.ylabel("Price ($)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

## Clean and dirty prices

Between coupon dates, the seller has earned part of the next coupon. Bond quotes show the **clean price**, without that **accrued interest**; the buyer actually pays the **dirty price** = clean + accrued.

```python run
semiannual_coupon = 1000 * 0.05 / 2
days_since_last, days_in_period = 73, 182
accrued = semiannual_coupon * days_since_last / days_in_period
clean = 1_012.40
print(f"Accrued interest: ${accrued:.2f}   Dirty (invoice) price: ${clean + accrued:,.2f}")
```

## Credit risk and spreads

Corporate bonds yield more than Treasuries of the same maturity. The difference, the **credit spread**, compensates for default risk and lower liquidity.

```python run
treasury_10y = 0.042
spreads = {"AAA": 0.006, "A": 0.010, "BBB": 0.015, "BB": 0.028, "B": 0.040, "CCC": 0.095}
print("Rating   Yield    Price of a 10y 5% bond")
for rating, spread in spreads.items():
    y = treasury_10y + spread
    print(f"{rating:<7} {y:6.2%}   ${bonds.bond_price(1000, 0.05, y, 10):8,.2f}")
```

The yield on a risky bond is a **promised** yield. If default is possible, the **expected** return is lower than the YTM.

## Key takeaways

- Bond price = PV of coupons (an annuity) + PV of face value (a lump sum).
- Prices and yields move **inversely**; long bonds are the most sensitive.
- Coupon > yield → premium; coupon < yield → discount; prices pull to par as maturity nears.
- YTM is the bond's IRR; credit spreads compensate for default and liquidity risk.

## Exercises

1. A 20-year bond with a 6% semi-annual coupon trades at $1,120. What is its YTM?
2. How much does a 30-year 4% bond's price fall if yields rise from 4% to 5%? Compare with a 2-year 4% bond.
3. A 5-year zero-coupon bond costs $780. What is its yield (annual compounding)?

<details>
<summary>Solutions</summary>

```python run
print(f"1. YTM: {bonds.yield_to_maturity(1120, 1000, 0.06, 20):.3%}")
for m in [30, 2]:
    change = bonds.bond_price(1000, 0.04, 0.05, m) / bonds.bond_price(1000, 0.04, 0.04, m) - 1
    print(f"2. {m}-year bond price change: {change:.2%}")
print(f"3. Zero yield: {(1000 / 780) ** (1 / 5) - 1:.3%}")
```

</details>

## Watch & read

- [watch] [Khan Academy: Stocks and bonds](https://www.khanacademy.org/economics-finance-domain/core-finance/stock-and-bonds). Bond pricing, yields and the price-yield relationship.
- [watch] [Yale ECON 252 (Shiller), lecture "Debt Markets: Term Structure"](https://oyc.yale.edu/economics/econ-252). How bond markets work and why yields differ by maturity.
- [read] [OpenStax *Principles of Finance*, Chapter 10: Bonds and Bond Valuation](https://openstax.org/details/books/principles-finance). Free chapter with practice problems.
- [data] [U.S. Treasury daily yield curve rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates). Today's Treasury yields at every maturity.
- [data] [FRED: ICE BofA corporate bond spreads](https://fred.stlouisfed.org/). Search for "BAMLC0A0CM" (investment grade) and "BAMLH0A0HYM2" (high yield) to see spreads over time.
