# Crypto Fetch

## Setup

Set CMC API key environment variable (Get free API key - https://coinmarketcap.com/api/)

```bash
# Linux / Mac
export COINMARKETCAP_API_KEY="<YOUR-CMC-API-KEY>"

# Windows (PowerShell)
$env:COINMARKETCAP_API_KEY="<YOUR-CMC-API-KEY>"
```

Create python environment

```bash
python -m venv venv
```

## Usages

### price command

Fetch the price of a single cryptocurrency (default fiat is EUR)

```bash
crypto-fetch price XRP
```

Fetch the price of multiple cryptocurrencies

```bash
crypto-fetch price XRP,BTC,HBAR
```

Fetch the price of a cryptocurrency in a specific fiat currency

```bash
crypto-fetch price XRP --currency USD

# short-hand
crypto-fetch price XRP -c USD
```

### convert command

Convert a specified amount of a cryptocurrency (default fiat is EUR)

```bash
crypto-fetch convert 500 --ticker XRP

# short-hand
crypto-fetch convert 500 -t XRP
```

Convert a specified amount of a cryptocurrency to a specified fiat currency

```bash
crypto-fetch convert 500 --ticker XRP --currency USD

# short-hand
crypto-fetch convert 500 -t XRP -c USD
```

Convert a list of cryptocurrencies to a specified fiat currency

```bash
crypto-fetch convert -f portfolio.txt
```
