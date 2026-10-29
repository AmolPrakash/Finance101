# Finance101

**An interactive finance textbook you can run in your browser.** Four courses (FIN 101, 102, 201 and 202) in 25 chapters. Every idea is explained in plain language, written as a formula, and implemented in Python that you can edit and run right on the page. Nothing to install, nothing to pay.

📖 **Read it here: https://amolprakash.github.io/Finance101/**

| Course | Chapters | Topics |
|---|---|---|
| **FIN 101** Foundations of Finance | 00–07 | Python primer, the financial system, time value of money, interest rates and inflation, annuities and loans, financial statements, ratio analysis, personal finance |
| **FIN 102** Corporate Finance & Valuation | 08–13 | NPV and IRR, project cash flows, bonds, stocks and DCF, cost of capital, capital structure and payout |
| **FIN 201** Investments | 14–18 | Risk and return, portfolio theory, CAPM and factor models, market efficiency, the yield curve and duration, performance evaluation |
| **FIN 202** Derivatives & Risk Management | 19–24 | Forwards, futures and swaps, options strategies, binomial trees, Black-Scholes and the Greeks, Monte Carlo and Value at Risk, behavioral finance, capstone project |

## How the book works

- **Read and run side by side.** Each chapter mixes explanation, math and editable code cells. Press Shift+Enter to run a cell; charts appear inline.
- **Scratchpad.** A Python editor that sits beside the text and shares the chapter's variables, so you can experiment while you read.
- **Code Lab.** Open and run *every* `.py` file in this repository in the browser: the `finance101` library, the example scripts and the full `pytest` suite. Edit a library function and see the examples and tests use your version.
- **Free resources.** Every chapter ends with free lectures (MIT, Yale, Khan Academy, NYU), free textbook chapters (OpenStax) and free data sources. A [resources page](https://amolprakash.github.io/Finance101/#/resources) collects them all.
- **Progress tracking.** Mark chapters complete; progress is saved in your browser.

Python runs entirely in your browser via [Pyodide](https://pyodide.org/) (CPython compiled to WebAssembly). The site is static and hosted free on GitHub Pages.

## Repository layout

```
Finance101/
├── book/                    # the interactive textbook (static site)
│   ├── chapters/            # one Markdown file per chapter; ```python run blocks become live cells
│   ├── assets/              # app.js (reader UI), py-worker.js (Pyodide), app.css
│   ├── toc.json             # course and chapter order
│   ├── build.py             # assembles the site into _site/
│   └── check_chapters.py    # runs every code cell in every chapter (used in CI)
├── finance101/              # the library: every formula as a short, documented function
├── examples/                # standalone scripts, runnable in the Code Lab or locally
├── tests/                   # pytest suite with known-answer checks
└── .github/workflows/       # tests, cell checks, then deploys to GitHub Pages
```

### The `finance101` library

Pure standard-library Python, so the math stays visible:

| Module | Covers |
|---|---|
| `time_value` | PV/FV, annuities, perpetuities, EAR, real rates, solving for rate and time |
| `loans` | Loan payments, amortization schedules |
| `statements` | Income statement, balance sheet, ratio analysis, DuPont |
| `capital_budgeting` | NPV, IRR, payback, profitability index |
| `project_cash_flows` | Operating and free cash flow, depreciation tax shields, salvage, EAA |
| `bonds` | Pricing, yield to maturity, duration, convexity |
| `equity` | Gordon growth, two-stage DDM, DCF, multiples |
| `capital_structure` | Modigliani-Miller, levered/unlevered beta, EPS, buybacks |
| `risk_return` | Returns, volatility, Sharpe, drawdown, VaR, expected shortfall |
| `portfolio` | Portfolio risk, minimum-variance and tangency portfolios, beta, CAPM, WACC |
| `yield_curve` | Discount factors, forward rates, bootstrapping |
| `performance` | Sortino, Treynor, Jensen's alpha, tracking error, information ratio |
| `derivatives` | Forward/futures pricing, FX forwards, hedge ratios, swaps |
| `options` | Payoffs, Black-Scholes, Greeks, implied volatility, strategies |
| `binomial` | CRR trees, American options, replication |
| `simulation` | Geometric Brownian motion, Monte Carlo pricing, Monte Carlo VaR |

## Run it locally

Requires Python 3.10+.

```bash
pip install -e ".[dev,book]"
```

Build and preview the book at http://localhost:8000:

```bash
python book/build.py --serve
```

Run the tests and check that every chapter's code cells still run:

```bash
pytest
```

```bash
python book/check_chapters.py
```

Run any example:

```bash
python examples/01_time_value_of_money.py
```

## Publishing (one-time setup)

The workflow in `.github/workflows/pages.yml` tests everything and deploys the site on every push to `main`. To turn it on, go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.

## Writing a chapter

Chapters are Markdown. Use `\( … \)` for inline math and `\[ … \]` for display math (so `$` stays a dollar sign), fence runnable code with ```` ```python run ````, and use GitHub-style callouts (`> [!TIP]`, `> [!IMPORTANT]`, `> [!NOTE]`, `> [!WARNING]`). Resource list items can start with a tag: `[watch]`, `[read]`, `[course]`, `[data]` or `[tool]`. Add the chapter to `book/toc.json`, then run `python book/check_chapters.py` to make sure every cell runs.

## Disclaimer

This book is for education. It is not investment, tax or legal advice.
