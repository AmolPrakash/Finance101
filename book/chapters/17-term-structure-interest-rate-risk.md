# The Yield Curve and Interest-Rate Risk

Chapter 10 priced a bond using a single yield. But money borrowed for one year and money borrowed for thirty years usually carry different rates. The relationship between maturity and yield, the **term structure of interest rates** or **yield curve**, is one of the most watched charts in finance. This chapter shows how to extract information from it and how to measure and manage a bond portfolio's sensitivity to rate changes.

> [!IMPORTANT]
> - **Spot rates** are yields on zero-coupon bonds; each maturity has its own.
> - **Forward rates** are the future borrowing rates implied by today's spot curve.
> - **Duration** measures how much a bond's price moves when rates change; **convexity** corrects for the curvature.

## Spot rates and discount factors

The **spot rate** \(s_t\) is the yield on a zero-coupon bond maturing at \(t\). It gives a **discount factor** for each date:

\[ DF_t = \frac{1}{(1 + s_t)^t} \]

The correct way to price any bond is to discount **each cash flow at the spot rate for its own date**:

\[ P = \sum_t CF_t \times DF_t \]

```python run
from finance101 import yield_curve as yc, bonds

spots = [0.040, 0.043, 0.045, 0.047, 0.048]          # years 1-5, annual compounding
for t, s in enumerate(spots, start=1):
    print(f"Year {t}: spot {s:.2%}, discount factor {yc.discount_factor(s, t):.5f}")

flows = [60, 60, 60, 60, 1060]                       # a 5-year 6% annual-coupon bond
price = yc.price_from_spot_curve(flows, spots)
ytm = bonds.yield_to_maturity(price, 1000, 0.06, 5, frequency=1)
print(f"\nPrice using the spot curve: ${price:,.2f}; its YTM is {ytm:.3%}")
```

The YTM is a kind of weighted average of the spot rates, dominated by the final payment.

## Bootstrapping the curve

We rarely observe zero-coupon yields directly; we observe prices of **coupon** bonds. **Bootstrapping** extracts spot rates one maturity at a time: the 1-year bond gives \(s_1\), the 2-year bond (using \(s_1\) for its first coupon) gives \(s_2\), and so on.

```python run
par_yields = [0.040, 0.0428, 0.0447, 0.0465, 0.0475, 0.0485, 0.049, 0.0495, 0.050, 0.0505]
spot_curve = yc.bootstrap_spot_rates(par_yields)
print("Maturity  Par yield  Spot rate")
for t, (p, s) in enumerate(zip(par_yields, spot_curve), start=1):
    print(f"{t:>8}  {p:>9.3%}  {s:>9.3%}")
```

When the curve slopes upward, spot rates sit above par yields at longer maturities, because a coupon bond's early coupons are discounted at the lower short rates.

## Forward rates

If the 1-year spot rate is 4% and the 2-year spot rate is 4.5%, then investing for two years at once must give the same result as investing for one year and **locking in** a rate for the second. That locked-in rate is the **forward rate**:

\[ (1 + s_2)^2 = (1 + s_1)(1 + f_{1,2}) \]

```python run
import matplotlib.pyplot as plt

forwards = [spot_curve[0]] + [yc.forward_rate(spot_curve[t - 1], t, spot_curve[t], t + 1) for t in range(1, len(spot_curve))]
years = list(range(1, len(spot_curve) + 1))
plt.plot(years, [p * 100 for p in par_yields], marker="o", label="Par yields")
plt.plot(years, [s * 100 for s in spot_curve], marker="o", label="Spot rates")
plt.step(years, [f * 100 for f in forwards], where="mid", label="1-year forward rates")
plt.title("Par, spot and forward curves")
plt.xlabel("Maturity (years)"); plt.ylabel("Rate (%)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

### What does the curve's shape mean?

- **Expectations hypothesis:** forward rates are the market's forecast of future short rates. An upward-sloping curve means rates are expected to rise.
- **Liquidity preference:** long bonds are riskier, so investors demand a **term premium**. The curve slopes up even if rates are expected to stay flat.
- An **inverted** curve (short rates above long rates) often means markets expect the central bank to cut rates, typically because a recession is coming. Inversions have preceded most US recessions since the 1960s.

```python run
shapes = {
    "Normal (upward)": [0.030, 0.034, 0.037, 0.040, 0.043, 0.045],
    "Flat": [0.045, 0.045, 0.045, 0.045, 0.045, 0.045],
    "Inverted": [0.055, 0.051, 0.047, 0.044, 0.042, 0.041],
}
maturities = [0.25, 1, 2, 5, 10, 30]
for name, curve in shapes.items():
    plt.plot(maturities, [y * 100 for y in curve], marker="o", label=name)
plt.xscale("log"); plt.xticks(maturities, ["3m", "1y", "2y", "5y", "10y", "30y"])
plt.title("Yield curve shapes (illustrative)")
plt.ylabel("Yield (%)"); plt.legend(); plt.grid(alpha=0.3)
plt.show()
```

## Duration: measuring interest-rate risk

**Macaulay duration** is the weighted-average time until you receive a bond's cash flows, with weights equal to each cash flow's share of the price:

\[ D_{Mac} = \sum_t t \times \frac{PV(CF_t)}{P} \]

**Modified duration** turns that into a price sensitivity:

\[ D_{Mod} = \frac{D_{Mac}}{1 + y/m} \qquad \frac{\Delta P}{P} \approx -D_{Mod}\,\Delta y \]

```python run
print(f"{'Bond':<26} {'Macaulay':>9} {'Modified':>9} {'DV01 ($)':>9}")
for label, coupon, years in [("2-year 5% coupon", 0.05, 2), ("10-year 5% coupon", 0.05, 10),
                             ("10-year 1% coupon", 0.01, 10), ("10-year zero", 0.0, 10), ("30-year 5% coupon", 0.05, 30)]:
    mac = bonds.macaulay_duration(1000, coupon, 0.05, years)
    mod = bonds.modified_duration(1000, coupon, 0.05, years)
    dv01 = mod * bonds.bond_price(1000, coupon, 0.05, years) * 0.0001
    print(f"{label:<26} {mac:>9.2f} {mod:>9.2f} {dv01:>9.3f}")
```

Duration is **longer** for longer maturities and for **lower coupons**. A zero's duration equals its maturity. **DV01** (dollar value of a basis point) is the price change for a 0.01% change in yield, the unit traders actually use.

## Convexity

Duration is a straight-line (first-order) approximation of a curved price-yield relationship. **Convexity** adds the curvature:

\[ \frac{\Delta P}{P} \approx -D_{Mod}\,\Delta y + \tfrac{1}{2}\,C\,(\Delta y)^2 \]

```python run
face, cpn, mat, y0 = 1000, 0.05, 30, 0.05
p0 = bonds.bond_price(face, cpn, y0, mat)
mod = bonds.modified_duration(face, cpn, y0, mat)
conv = bonds.convexity(face, cpn, y0, mat)

shifts = [i / 1000 for i in range(-30, 31)]
actual = [bonds.bond_price(face, cpn, y0 + dy, mat) for dy in shifts]
dur_only = [p0 * (1 - mod * dy) for dy in shifts]
dur_conv = [p0 * (1 - mod * dy + 0.5 * conv * dy ** 2) for dy in shifts]

plt.plot([s * 100 for s in shifts], actual, label="Actual price", linewidth=2.5)
plt.plot([s * 100 for s in shifts], dur_only, "--", label="Duration only")
plt.plot([s * 100 for s in shifts], dur_conv, ":", label="Duration + convexity")
plt.title("30-year 5% bond: approximating price changes")
plt.xlabel("Change in yield (percentage points)"); plt.ylabel("Price ($)")
plt.legend(); plt.grid(alpha=0.3)
plt.show()

for dy in [-0.02, 0.02]:
    exact = bonds.bond_price(face, cpn, y0 + dy, mat) / p0 - 1
    print(f"Δy {dy:+.0%}: actual {exact:+.2%}, duration {-mod * dy:+.2%}, duration+convexity {-mod * dy + 0.5 * conv * dy ** 2:+.2%}")
```

Positive convexity is good for bondholders: prices rise **more** when yields fall than they drop when yields rise.

## Immunization: protecting against rate changes

A pension fund owes $10 million in 7 years. If it buys bonds with a **duration equal to the liability's duration (7 years)**, small parallel rate changes affect both sides almost equally. Lower rates raise the value of the assets, higher rates raise the reinvestment income, and the two effects offset. This is **immunization**.

```python run
liability, horizon, y = 10_000_000, 7, 0.05
pv_liability = liability / (1 + y) ** horizon

short = dict(coupon=0.05, years=3)
long = dict(coupon=0.05, years=15)
d_short = bonds.macaulay_duration(1000, short["coupon"], y, short["years"], frequency=1)
d_long = bonds.macaulay_duration(1000, long["coupon"], y, long["years"], frequency=1)
w_short = (d_long - horizon) / (d_long - d_short)          # solve w*d_short + (1-w)*d_long = 7
print(f"Durations: short {d_short:.2f}, long {d_long:.2f} → {w_short:.1%} short / {1 - w_short:.1%} long")

units_short = w_short * pv_liability / bonds.bond_price(1000, short["coupon"], y, short["years"], frequency=1)
units_long = (1 - w_short) * pv_liability / bonds.bond_price(1000, long["coupon"], y, long["years"], frequency=1)

print(f"\n{'Rate shift':>10} {'Assets':>14} {'Liability':>14} {'Surplus':>10}")
for dy in [-0.02, -0.01, 0.0, 0.01, 0.02]:
    yy = y + dy
    assets = (units_short * bonds.bond_price(1000, short["coupon"], yy, short["years"], frequency=1)
              + units_long * bonds.bond_price(1000, long["coupon"], yy, long["years"], frequency=1))
    liab = liability / (1 + yy) ** horizon
    print(f"{dy:>+10.0%} {assets:>14,.0f} {liab:>14,.0f} {assets - liab:>10,.0f}")
```

The surplus stays near zero, and is slightly positive for big moves because the bond portfolio has more convexity than the liability. Immunization must be **rebalanced** as time passes and rates move, and it only protects against **parallel** shifts of the curve.

## Key takeaways

- Price bonds with **spot rates**; **bootstrap** them from coupon bond yields.
- **Forward rates** are implied future rates; the curve's shape reflects rate expectations and term premiums.
- **Modified duration** ≈ % price change per 1 point of yield; **DV01** is the dollar change per basis point.
- **Convexity** makes price gains larger than losses for equal rate moves.
- **Immunization** matches asset and liability durations to neutralize small parallel rate shifts.

## Exercises

1. With 1-year spot 3.5% and 3-year spot 4.2%, what is the 2-year rate starting one year from now?
2. A bond portfolio worth $50 million has a modified duration of 6.3. Estimate the dollar loss if yields rise 0.75%.
3. Which has the higher duration, a 20-year 8% coupon bond or a 15-year zero-coupon bond? Check with code (5% yield, annual payments).

<details>
<summary>Solutions</summary>

```python run
print(f"1. f(1,3) = {yc.forward_rate(0.035, 1, 0.042, 3):.3%}")
print(f"2. Loss ≈ ${50e6 * 6.3 * 0.0075:,.0f}")
print(f"3. 20y 8% coupon: {bonds.macaulay_duration(1000, 0.08, 0.05, 20, frequency=1):.2f} years;"
      f" 15y zero: {bonds.macaulay_duration(1000, 0.0, 0.05, 15, frequency=1):.2f} years")
```

</details>

## Watch & read

- [watch] [Yale ECON 252 (Shiller), lecture "Debt Markets: Term Structure"](https://oyc.yale.edu/economics/econ-252). The expectations hypothesis and term premiums with real data.
- [watch] [MIT 15.401 Finance Theory I](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/). The "Fixed-Income Securities" lectures cover spot rates, forwards and duration.
- [data] [FRED: 10-year minus 2-year Treasury spread (T10Y2Y)](https://fred.stlouisfed.org/series/T10Y2Y). Watch the yield curve invert before recessions.
- [data] [U.S. Treasury daily par yield curve](https://home.treasury.gov/resource-center/data-chart-center/interest-rates). Bootstrap today's spot curve from it.
- [read] [Investopedia: Yield Curve](https://www.investopedia.com/terms/y/yieldcurve.asp) and [Duration](https://www.investopedia.com/terms/d/duration.asp). Short references.
