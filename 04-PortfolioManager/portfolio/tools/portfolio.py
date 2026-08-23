try:
    import httpx
except ImportError:
    raise ImportError("The 'httpx' module is required. Run 'pip install httpx' to install the library.")

from typing import Any

from agno.tools import Toolkit

FRANKFURTER_BASE_URL = "https://api.frankfurter.app"


class PortfolioTools(Toolkit):
    def __init__(self, **kwargs: Any):  # pyright: ignore[reportExplicitAny]
        tools = [
            self.get_allocation_weights,
            self.get_portfolio_return,
            self.convert_currency,
        ]

        super().__init__(name="portfolio_tool", tools=tools, **kwargs)  # pyright: ignore[reportAny]

    def get_allocation_weights(self, portfolio_value: float, allocations: str) -> str:
        """
        Compute the dollar amount per asset class for a target allocation.

        Args:
            portfolio_value (float): Total portfolio value in dollars.
            allocations (str): Comma-separated "name:percent" pairs, e.g. "stocks:60,bonds:30,cash:10".

        Returns:
            str: Each sleeve's weight and dollar amount.
        """
        try:
            rows: list[str] = []
            total = 0.0
            for pair in allocations.split(","):
                name, _, percent = pair.strip().partition(":")
                weight = float(percent)
                amount = portfolio_value * weight / 100.0
                total += weight
                rows.append(f"{name.strip()}: {weight:.1f}% = ${amount:,.2f}")

            if abs(total - 100.0) > 0.01:
                rows.append(f"WARNING: weights sum to {total:.1f}%, not 100%")
            return "\n".join(rows)
        except ValueError as e:
            return f"Invalid allocation format: {e}"

    def get_portfolio_return(self, weights: str, returns: str) -> str:
        """
        Compute the weighted expected return of a portfolio.

        Args:
            weights (str): Comma-separated weights in percent, e.g. "60,30,10".
            returns (str): Comma-separated expected returns in percent, e.g. "8,4,2".

        Returns:
            str: The weighted portfolio return as a percentage.
        """
        try:
            w = [float(x) for x in weights.split(",")]
            r = [float(x) for x in returns.split(",")]
            if len(w) != len(r):
                return "Error: weights and returns must have the same number of values"
            total_weight = sum(w)
            if total_weight == 0:
                return "Error: weights sum to zero"
            expected = sum((wi / total_weight) * ri for wi, ri in zip(w, r))
            return f"Expected portfolio return: {expected:.2f}%"
        except ValueError as e:
            return f"Invalid input format: {e}"

    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> str:
        """
        Convert an amount between currencies using the Frankfurter API (ECB rates).

        Args:
            amount (float): The amount to convert.
            from_currency (str): Source currency code, e.g. "USD".
            to_currency (str): Target currency code, e.g. "EUR".

        Returns:
            str: The converted amount and the exchange rate used.
        """
        try:
            response = httpx.get(
                f"{FRANKFURTER_BASE_URL}/latest",
                params={"amount": amount, "from": from_currency, "to": to_currency},
            )
            _ = response.raise_for_status()
            data = response.json()
            rates = data.get("rates", {})
            if to_currency not in rates:
                return f"No rate found for {from_currency} -> {to_currency}"
            converted = rates[to_currency]
            rate = converted / amount if amount else 0.0
            return f"{amount:,.2f} {from_currency} = {converted:,.2f} {to_currency} (rate: {rate:.4f})"
        except httpx.HTTPStatusError as e:
            return f"HTTP error occurred: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
