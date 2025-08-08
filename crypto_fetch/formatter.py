import math
from typing import List

from crypto_fetch.constants import CURRENCY_SYMBOL_MAP
from crypto_fetch.constants import CURRENCY_CODE_ONLY_MAP
from crypto_fetch.constants import BOLD_OUTPUT
from crypto_fetch.constants import RESET_OUTPUT
from crypto_fetch.constants import RED_OUTPUT
from crypto_fetch.constants import GREEN_OUTPUT

def format_price_output(data, currency_code: str, api_url: str, verbose: bool) -> str:
    """
    Formats the cryptocurrency price data received from the API.

    :param data: The parsed data received from the API.
    :param currency_code: The fiat currency code.
    :param api_url: The API URL.
    :verbose: Whether or not the output should be verbose.

    :returns: Formatted output string.
    """
    if not data:
        return "❌ No data available"
    
    output: List[str] = []
    currency_code: str = currency_code.upper()
    currency_symbol: str = _get_currency_symbol(currency_code)

    for ticker, data in data.items():
        price: float = data.get("price", 0)
        base_line: str = _get_base_price_output(price, ticker, currency_symbol, currency_code)

        if not verbose:
            # base output
            output.append(base_line)
            continue
        
        # verbose output
        verbose_details: List[str] = _get_verbose_price_output(data, currency_code)
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
        return f"🔹 ${ticker}: {BOLD_OUTPUT}{currency_symbol}{price:.4f}{RESET_OUTPUT} ({currency_code})"
    elif currency_code in CURRENCY_CODE_ONLY_MAP:
        return f"🔹 ${ticker}: {BOLD_OUTPUT}{price:.4f}{currency_symbol}{RESET_OUTPUT} ({currency_code})"
    else:
        return f"🔹 ${ticker}: {BOLD_OUTPUT}{currency_symbol}{price:.4f}{RESET_OUTPUT}"
    
def _get_verbose_price_output(data, currency_code: str) -> List[str]:
    """
    Gets the verbose output for a cryptocurrency.

    :param data: The parsed data received from the API.
    :param currency_code: The fiat currency code.

    :return: The verbose out as a list of strs.
    """
    verbose_details: List[str] = []

    change_1hr: str = data.get("1h_change", 0)
    change_24hr: str = data.get("24h_change", 0)
    market_cap: str = data.get("market_cap", 0)
    volume_24hr: str = data.get("24h_volume", 0)

    verbose_details.append(f"\t> 1hr Change:  {_format_percentage_change(change_1hr)}")
    verbose_details.append(f"\t> 24hr Change: {_format_percentage_change(change_24hr)}")
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
        output: str = f"🔸 {amount_to_convert} ${ticker} => {BOLD_OUTPUT}{currency_symbol}{converted_amount:.4f}{RESET_OUTPUT} ({currency_code})"
    elif currency_code in CURRENCY_CODE_ONLY_MAP:
        output: str = f"🔸 {amount_to_convert} ${ticker} => {BOLD_OUTPUT}{converted_amount:.4f}{currency_symbol}{RESET_OUTPUT} ({currency_code})"
    else:
        output: str = f"🔸 {amount_to_convert} ${ticker} => {BOLD_OUTPUT}{currency_symbol}{converted_amount:.4f}{RESET_OUTPUT}"

    return output

def _format_large_number(number: float, currency_code: str) -> str:
    """
    Formats a large number with units (K, M, B, T).

    :param number: The number to format.
    :param currency_code: The currency code.

    :returns: The formatted number as a str.
    """
    magnitude: int = int(math.floor(math.log10(abs(number)) / 3))
    units: List[str] = ["", "K", "M", "B", "T"]
    unit: str = units[magnitude] if magnitude < len(units) else f"e{magnitude*3}"
    
    scaled: float = number / (10 ** (3 * magnitude))
    
    if scaled < 10:
        precision = 2
    elif scaled < 100:
        precision = 1
    else:
        precision = 0
    
    return f"{scaled:,.{precision}f}{unit} ({currency_code})"


def _format_percentage_change(change: float) -> str:
    """
    Formats a percentage change value.

    :param change: The percentage change.

    :returns: The formatted percentage str.
    """
    if change > 0:
        return f"{GREEN_OUTPUT}▲{RESET_OUTPUT} {change:.2f}%"
    elif change < 0:
        return f"{RED_OUTPUT}▼{RESET_OUTPUT} {change:.2f}%"
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