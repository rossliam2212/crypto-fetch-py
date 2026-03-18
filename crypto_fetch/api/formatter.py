import math
from typing import Dict, List

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from crypto_fetch.commands.command_utils import get_timestamp
from crypto_fetch.constants import (
    BOLD,
    CURRENCY_CODE_ONLY_MAP,
    CURRENCY_SYMBOL_MAP,
    GREEN,
    PRECISION_HIGH,
    PRECISION_LOW,
    PRECISION_MEDIUM,
    RED,
    RESET,
)

_console = Console()

def format_price_output(data: Dict[str, Dict[str, float]], currency_code: str, api_url: str, verbose: bool) -> str:
    """
    Formats the cryptocurrency price data received from the API.

    :param data: The parsed data received from the API.
    :param currency_code: The fiat currency code.
    :param api_url: The API URL.
    :param verbose: Whether the output should be verbose.

    :returns: Formatted output string.
    """
    if not data:
        return "❌ No data available"
    
    output: List[str] = []
    currency_code: str = currency_code.upper()
    currency_symbol: str = _get_currency_symbol(currency_code)

    for ticker, ticker_data in data.items():
        price: float = ticker_data.get("price", 0)
        base_line: str = _get_base_price_output(price, ticker, currency_symbol, currency_code)

        if not verbose:
            # base output
            output.append(base_line)
            continue
        
        # verbose output
        verbose_details: List[str] = _get_verbose_price_output(ticker_data, currency_code)
        output.append(f"{base_line}\n  " + "\n  ".join(verbose_details))

    if verbose:
        output.append(f"\n[data fetched from '{api_url}']")

    return "\n".join(output)


def _get_base_price_output(price: float, ticker: str, currency_symbol: str, currency_code: str) -> str:
    """
    Gets the base output for a cryptocurrency.
    e.g. 🔹 $XRP: €2.6894

    :param price: The price of cryptocurrency.
    :param ticker: The ticker of the cryptocurrency.
    :param currency_symbol: The fiat currency symbol.
    :param currency_code: The fiat currency code.

    :return: The base output as a str.
    """
    if currency_symbol == "$" or currency_symbol == "¥":
        return f"🔹 ${ticker}: {BOLD}{currency_symbol}{price:.4f}{RESET} ({currency_code})"
    elif currency_code in CURRENCY_CODE_ONLY_MAP:
        return f"🔹 ${ticker}: {BOLD}{price:.4f}{currency_symbol}{RESET} ({currency_code})"
    else:
        return f"🔹 ${ticker}: {BOLD}{currency_symbol}{price:.4f}{RESET}"


def _get_verbose_price_output(data: Dict[str, float], currency_code: str) -> List[str]:
    """
    Gets the verbose output for a cryptocurrency.

    :param data: The parsed data received from the API.
    :param currency_code: The fiat currency code.

    :return: The verbose out as a list of strs.
    """
    verbose_details: List[str] = []

    change_1hr = data.get("1h_change")
    change_24hr: float = data.get("24h_change", 0)
    change_7d = data.get("7d_change")
    market_cap: float = data.get("market_cap", 0)
    volume_24hr: float = data.get("24h_volume", 0)

    if change_1hr is not None:
        verbose_details.append(f"\t> 1hr Change:  {_format_percentage_change(change_1hr)}")
    verbose_details.append(f"\t> 24hr Change: {_format_percentage_change(change_24hr)}")
    if change_7d is not None:
        verbose_details.append(f"\t> 7d Change:   {_format_percentage_change(change_7d)}")
    verbose_details.append(f"\t> 24hr Volume: {_format_large_number(volume_24hr, currency_code)}")
    verbose_details.append(f"\t> Market Cap:  {_format_large_number(market_cap, currency_code)}")

    return verbose_details


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
        output: str = f"🔸 {amount_to_convert} ${ticker} => {BOLD}{currency_symbol}{converted_amount:.4f}{RESET} ({currency_code})"
    elif currency_code in CURRENCY_CODE_ONLY_MAP:
        output: str = f"🔸 {amount_to_convert} ${ticker} => {BOLD}{converted_amount:.4f}{currency_symbol}{RESET} ({currency_code})"
    else:
        output: str = f"🔸 {amount_to_convert} ${ticker} => {BOLD}{currency_symbol}{converted_amount:.4f}{RESET}"

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
        return f"{GREEN}▲{RESET} {change:.2f}%"
    elif change < 0:
        return f"{RED}▼{RESET} {change:.2f}%"
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