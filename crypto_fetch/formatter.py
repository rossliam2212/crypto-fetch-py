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
            base_line = f"🔹 ${ticker}: {currency_symbol}{price} ({currency_code})"
        elif currency_code in CURRENCY_CODE_ONLY_MAP:
            base_line = f"🔹 ${ticker}: {price}{currency_symbol} ({currency_code})"
        else:
            base_line = f"🔹 ${ticker}: {currency_symbol}{price}"

        if not verbose:
            output.append(base_line)
            continue

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