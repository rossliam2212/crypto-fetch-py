def format_price_output(data, currency, verbose):
    """
    Formats the cryptocurrency data received from the CMC API.

    Args:
        data (dict): The data received from the CMC API.
        currency (str): The fiat currency to use.
        verbose (bool): Whether or not the output should be verbose.

    Returns:
        Formatted output string
    """
    if not data:
        return "No data available"
    
    output = []
    currency = currency.upper()
    currency_symbol = _get_currency_symbol(currency)

    for ticker, data in data.items():
        price = data.get("price", 0)
        base_line = f"> ${ticker}: {price} {currency}"

        if not verbose:
            output.append(base_line)
            continue

    return "\n".join(output)

def _get_currency_symbol(currency):
    """
    Get the symbol corresponding to the fiat currency

    Args:
        currency: The fiat currency whose symbol is wanted
    
    Returns:
        The fiat currencies symbol
    """
    # TODO Implement