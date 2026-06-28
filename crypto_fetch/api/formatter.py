import math
from typing import Dict, List, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


from crypto_fetch.commands.command_utils import get_timestamp
from crypto_fetch.constants import (
    CURRENCY_CODE_ONLY_MAP,
    CURRENCY_SYMBOL_MAP,
    PRECISION_HIGH,
    PRECISION_LOW,
    PRECISION_MEDIUM,
)

_console = Console(highlight=False)


def print_output(text: str) -> None:
    """Prints formatted output via rich console."""
    _console.print(text)

def format_price_output(data: Dict[str, Dict[str, float]], currency_code: str, api_url: str, verbose: bool) -> Optional[str]:
    """
    Formats the cryptocurrency price data received from the API.

    :param data: The parsed data received from the API.
    :param currency_code: The fiat currency code.
    :param api_url: The API URL.
    :param verbose: Whether the output should be verbose.

    :returns: Formatted output string, or None if verbose (prints directly).
    """
    if not data:
        return "❌ No data available"

    currency_code: str = currency_code.upper()
    currency_symbol: str = _get_currency_symbol(currency_code)

    if not verbose:
        output: List[str] = []
        for ticker, ticker_data in data.items():
            price: float = ticker_data.get("price", 0)
            output.append(_get_base_price_output(price, ticker, currency_symbol, currency_code))
        return "\n".join(output)

    for ticker, ticker_data in data.items():
        price: float = ticker_data.get("price", 0)
        price_str = _format_price(price, currency_symbol, currency_code)
        _print_verbose_price_table(ticker, price_str, ticker_data, currency_code)

    _console.print(f"[dim]data fetched from '{api_url}'[/dim]\n")
    return None


def _format_price(price: float, currency_symbol: str, currency_code: str) -> str:
    if currency_symbol in ("$", "¥"):
        return f"{currency_symbol}{price:.4f} ({currency_code})"
    elif currency_code in CURRENCY_CODE_ONLY_MAP:
        return f"{price:.4f}{currency_symbol} ({currency_code})"
    else:
        return f"{currency_symbol}{price:.4f}"


def _get_base_price_output(price: float, ticker: str, currency_symbol: str, currency_code: str) -> str:
    price_str = _format_price(price, currency_symbol, currency_code)
    return f"🔹 [bold]${ticker}[/bold]: [bold cyan]{price_str}[/bold cyan]"


def _print_verbose_price_table(ticker: str, price_str: str, data: Dict[str, float], currency_code: str) -> None:
    change_1hr = data.get("1h_change")
    change_24hr: float = data.get("24h_change", 0)
    change_7d = data.get("7d_change")
    volume_24hr: float = data.get("24h_volume", 0)
    market_cap: float = data.get("market_cap", 0)

    _console.print(f"[bold]${ticker}[/bold]  [bold cyan]{price_str}[/bold cyan]")
    _console.rule(style="dim")

    rows = []
    if change_1hr is not None:
        rows.append(("1h Change", _format_percentage_change(change_1hr)))
    rows.append(("24h Change", _format_percentage_change(change_24hr)))
    if change_7d is not None:
        rows.append(("7d Change", _format_percentage_change(change_7d)))
    rows.append(("24h Volume", _format_large_number(volume_24hr, currency_code)))
    rows.append(("Market Cap", _format_large_number(market_cap, currency_code)))

    for label, value in rows:
        _console.print(f"  [dim]{label:<12}[/dim]{value}")

    _console.print()


def format_convert_output(ticker: str, currency_code: str, amount_to_convert: float, converted_amount: float) -> str:
    """
    Formats the output for the convert command.
    
    :param ticker: The cryptocurrency ticker.
    :param currency_code: The fiat currency code.
    :param amount_to_convert: The amount of cryptocurrency to convert.
    :param converted_amount: The convert price.

    :returns: Formatted output string.
    """
    currency_code: str = currency_code.upper()
    currency_symbol: str = _get_currency_symbol(currency_code)

    if currency_symbol == "$" or currency_symbol == "¥":
        output: str = f"🔸 {amount_to_convert} ${ticker} => [bold]{currency_symbol}{converted_amount:.4f}[/bold] ({currency_code})"
    elif currency_code in CURRENCY_CODE_ONLY_MAP:
        output: str = f"🔸 {amount_to_convert} ${ticker} => [bold]{converted_amount:.4f}{currency_symbol}[/bold] ({currency_code})"
    else:
        output: str = f"🔸 {amount_to_convert} ${ticker} => [bold]{currency_symbol}{converted_amount:.4f}[/bold]"

    return output


def format_portfolio_output(holdings: Dict[str, float], price_data: Dict[str, Dict[str, float]], currency_code: str) -> None:
    """
    Renders the portfolio holdings table and summary panel.

    :param holdings: Map of ticker -> amount held.
    :param price_data: Map of ticker -> price data from API.
    :param currency_code: The fiat currency code.
    """
    currency_code = currency_code.upper()
    symbol = _get_currency_symbol(currency_code)

    console = _console

    table = Table(title="Portfolio Holdings", box=box.HEAVY_HEAD, show_footer=False)
    table.add_column("Asset", style="bold")
    table.add_column("Holding", justify="right")
    table.add_column("Value", justify="right")
    table.add_column("Spot Price", justify="right")

    total_value = 0.0
    for ticker, amount in holdings.items():
        price = price_data.get(ticker, {}).get("price", 0.0)
        value = amount * price
        total_value += value

        if symbol in ("$", "¥"):
            value_str = f"{symbol}{value:,.2f}"
            price_str = f"{symbol}{price:,.2f}"
        else:
            value_str = f"{value:,.2f} {symbol}"
            price_str = f"{price:,.2f} {symbol}"

        table.add_row(ticker, str(amount), value_str, price_str)

    console.print(table)

    summary = (
        f"Total Assets: {len(holdings)}\n"
        f"Total Value:  {f'{symbol}{total_value:,.2f}' if symbol in ('$', '¥') else f'{total_value:,.2f} {symbol}'}\n"
        "\n"
        f"Timestamp:    {get_timestamp()}"
    )
    console.print(Panel(summary, title="Portfolio Summary", expand=False))


def _format_large_number(number: float, currency_code: str) -> str:
    """
    Formats a large number with units (K, M, B, T).

    :param number: The number to format.
    :param currency_code: The currency code.

    :returns: The formatted number as a str.
    """
    if number == 0:
        return f"0 ({currency_code})"

    magnitude: int = int(math.floor(math.log10(abs(number)) / 3))
    units: List[str] = ["", "K", "M", "B", "T"]
    unit: str = units[magnitude] if magnitude < len(units) else f"e{magnitude*3}"
    
    scaled: float = number / (10 ** (3 * magnitude))
    
    if scaled < 10:
        precision = PRECISION_HIGH
    elif scaled < 100:
        precision = PRECISION_MEDIUM
    else:
        precision = PRECISION_LOW
    
    return f"{scaled:,.{precision}f}{unit} ({currency_code})"


def _format_percentage_change(change: float) -> str:
    """
    Formats a percentage change value.

    :param change: The percentage change.

    :returns: The formatted percentage str.
    """
    if change > 0:
        return f"[green]▲[/green] {change:.2f}%"
    elif change < 0:
        return f"[red]▼[/red] {change:.2f}%"
    else:
        return f"{change:.2f}%"


def _get_currency_symbol(currency: str) -> str:
    """
    Get the symbol corresponding to a fiat currency.

    :param currency: The fiat currency code.
    
    :returns: The fiat currencies symbol.
    """
    if currency in CURRENCY_SYMBOL_MAP:
        return CURRENCY_SYMBOL_MAP[currency]
    else:
        return "[/]"