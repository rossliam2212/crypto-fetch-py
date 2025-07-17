import math

from crypto_fetch.constants import CURRENCY_SYMBOL_MAP
from crypto_fetch.constants import CURRENCY_CODE_ONLY_MAP

def format_price_output(data, currency_code, verbose):
    """
    Formats the cryptocurrency price data received from the CMC API.

    Args:
        - data (dict): The data received from the CMC API formatted.
        - currency_code (str): The fiat currency code.
        - verbose (bool): Whether or not the output should be verbose.

    Returns:
        - Formatted output string.
    """
    if not data:
        return "❌ No data available"
    
    output = []
    currency_code = currency_code.upper()
    currency_symbol = _get_currency_symbol(currency_code)

    for ticker, data in data.items():
        price = data.get("price", 0)
        
        if currency_symbol == "$" or currency_symbol == "¥":
            base_line = f"🔹 ${ticker}: {currency_symbol}{price:.2f} ({currency_code})"
        elif currency_code in CURRENCY_CODE_ONLY_MAP:
            base_line = f"🔹 ${ticker}: {price:.2f}{currency_symbol} ({currency_code})"
        else:
            base_line = f"🔹 ${ticker}: {currency_symbol}{price}"

        if not verbose:
            # base output
            output.append(base_line)
            continue
        
        # verbose output
        verbose_details = []
        change_1hr = data.get("1h_change", 0)
        change_24hr = data.get("24h_change", 0)

        verbose_details.append(f"\t> 1hr Change: {_format_percentage_change(change_1hr)}")
        verbose_details.append(f"\t> 24hr Change: {_format_percentage_change(change_24hr)}")

        market_cap = data.get("market_cap", 0)
        verbose_details.append(f"\t> Market Cap: {_format_large_number(market_cap, currency_code)}")

        volume_24hr = data.get("24h_volume", 0)

        output.append(f"{base_line}\n  " + "\n  ".join(verbose_details))

    return "\n".join(output)

def format_convert_output(ticker, currency_code, amount_to_convert, converted_amount):
    """
    Formats the output for the convert command.
    
    Args:
    - ticker (str): The cryptocurrency ticker.
    - currency_code (str): The fiat currency code.
    - amount_to_convert (float): The amount of cryptocurrency to convert.
    - converted_amount (float): The convert price.

    Returns:
        - Formattde output string.
    """
    currency_code = currency_code.upper()
    currency_symbol = _get_currency_symbol(currency_code)

    if currency_symbol == "$" or currency_symbol == "¥":
        output = f"🔸 {amount_to_convert} ${ticker} => {currency_symbol}{converted_amount} ({currency_code})"
    elif currency_code in CURRENCY_CODE_ONLY_MAP:
        output = f"🔸 {amount_to_convert} ${ticker} => {converted_amount}{currency_symbol} ({currency_code})"
    else:
        output = f"🔸 {amount_to_convert} ${ticker} => {currency_symbol}{converted_amount}"

    return output

def _format_large_number(number, currency_code):
    """
    Formats a large number with units (K, M, B, T).

    Args:
        - number (float): The number to format.
        - currency_code (str): The currency code.

    Returns:
        - The formatted number.
    """
    magnitude = int(math.floor(math.log10(abs(number)) / 3))
    units = ["", "K", "M", "B", "T"]
    unit = units[magnitude] if magnitude < len(units) else f"e{magnitude*3}"
    
    scaled = number / (10 ** (3 * magnitude))
    
    if scaled < 10:
        precision = 2
    elif scaled < 100:
        precision = 1
    else:
        precision = 0
    
    return f"{scaled:,.{precision}f}{unit} ({currency_code})"


def _format_percentage_change(change):
    """
    Formats a percentage change value.

    Args:
        - change (float): The percentage change.

    Returns:
        - The formatted percentage str.
    """
    if change > 0:
        return f"▲ {change:.2f}%"
    elif change < 0:
        return f"▼ {change:.2f}%"
    else:
        return f"{change:.2f}%"

def _get_currency_symbol(currency):
    """
    Get the symbol corresponding to a fiat currency.

    Args:
        - currency (str): The fiat currency code.
    
    Returns:
        - The fiat currencies symbol.
    """
    # TODO Add error handling
    if currency in CURRENCY_SYMBOL_MAP:
        return CURRENCY_SYMBOL_MAP[currency]