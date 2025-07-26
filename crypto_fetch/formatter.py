import math
from typing import List

from crypto_fetch.constants import CURRENCY_SYMBOL_MAP
from crypto_fetch.constants import CURRENCY_CODE_ONLY_MAP

def format_price_output(data, currency_code: str, verbose: bool) -> str:
    """
    Formats the cryptocurrency price data received from the CMC API.

    :param data: The data received from the CMC API formatted.
    :param currency_code: The fiat currency code.
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
        
        if currency_symbol == "$" or currency_symbol == "¥":
            base_line: str = f"🔹 ${ticker}: {currency_symbol}{price:.4f} ({currency_code})"
        elif currency_code in CURRENCY_CODE_ONLY_MAP:
            base_line: str = f"🔹 ${ticker}: {price:.4f}{currency_symbol} ({currency_code})"
        else:
            base_line: str = f"🔹 ${ticker}: {currency_symbol}{price:.4f}"

        if not verbose:
            # base output
            output.append(base_line)
            continue
        
        # verbose output
        verbose_details: List[str]= []
        change_1hr: str = data.get("1h_change", 0)
        change_24hr: str = data.get("24h_change", 0)

        verbose_details.append(f"\t> 1hr Change: {_format_percentage_change(change_1hr)}")
        verbose_details.append(f"\t> 24hr Change: {_format_percentage_change(change_24hr)}")

        market_cap: str = data.get("market_cap", 0)
        verbose_details.append(f"\t> Market Cap: {_format_large_number(market_cap, currency_code)}")

        volume_24hr: str = data.get("24h_volume", 0)

        output.append(f"{base_line}\n  " + "\n  ".join(verbose_details))

    return "\n".join(output)

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
        output: str = f"🔸 {amount_to_convert} ${ticker} => {currency_symbol}{converted_amount} ({currency_code})"
    elif currency_code in CURRENCY_CODE_ONLY_MAP:
        output: str = f"🔸 {amount_to_convert} ${ticker} => {converted_amount}{currency_symbol} ({currency_code})"
    else:
        output: str = f"🔸 {amount_to_convert} ${ticker} => {currency_symbol}{converted_amount}"

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
        return f"▲ {change:.2f}%"
    elif change < 0:
        return f"▼ {change:.2f}%"
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