"""Chapter 13 - Capital structure.

How should a firm mix debt and equity? Modigliani-Miller says it doesn't
matter in a perfect world; taxes, bankruptcy costs and incentives explain why
it does in the real one.
"""


def levered_value(unlevered_value: float, debt: float, tax_rate: float) -> float:
    """MM with corporate taxes: V_L = V_U + t x D (value of the interest tax shield)."""
    return unlevered_value + tax_rate * debt


def cost_of_equity_levered(unlevered_cost: float, cost_of_debt: float, debt_to_equity: float,
                           tax_rate: float = 0.0) -> float:
    """MM Proposition II: r_E = r_U + (D/E)(r_U - r_D)(1 - t)

    More debt makes equity riskier, so shareholders demand more.
    """
    return unlevered_cost + debt_to_equity * (unlevered_cost - cost_of_debt) * (1 - tax_rate)


def levered_beta(unlevered_beta: float, debt_to_equity: float, tax_rate: float) -> float:
    """Hamada: beta_L = beta_U x [1 + (1 - t) D/E]"""
    return unlevered_beta * (1 + (1 - tax_rate) * debt_to_equity)


def unlevered_beta(levered_beta_value: float, debt_to_equity: float, tax_rate: float) -> float:
    """Strip out financial leverage to get the business (asset) risk."""
    return levered_beta_value / (1 + (1 - tax_rate) * debt_to_equity)


def earnings_per_share(ebit: float, interest: float, tax_rate: float, shares: float) -> float:
    """EPS = (EBIT - Interest)(1 - t) / shares"""
    return (ebit - interest) * (1 - tax_rate) / shares


def share_price_after_buyback(equity_value: float, shares: float, cash_used: float) -> tuple:
    """A buyback at a fair price leaves the share price unchanged.

    Returns (new_share_price, new_share_count).
    """
    price = equity_value / shares
    repurchased = cash_used / price
    return (equity_value - cash_used) / (shares - repurchased), shares - repurchased
