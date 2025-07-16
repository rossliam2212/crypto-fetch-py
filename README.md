# crypto-fetch

Cli tool for fetching the latest cryptocurrency price data using the CoinMarketCap API.

Get free CMC API key here - [coinmarketcap.com/api/](https://coinmarketcap.com/api/)

## Setup

---

Set CMC API key environment variable

```bash
# Linux / Mac
export COINMARKETCAP_API_KEY="<YOUR-CMC-API-KEY>"

# Windows (PowerShell)
$env:COINMARKETCAP_API_KEY="<YOUR-CMC-API-KEY>"
```

## Usages

---

### price command

---

Fetch the price of a single cryptocurrency (default fiat is EUR)

```bash
$ crypto-fetch price XRP
FETCHING PRICE DATA FOR TICKER(S): XRP
🔹 $XRP: €2.6195152227194702
```

Fetch the price of multiple cryptocurrencies

```bash
$ crypto-fetch price XRP,BTC,XLM,ETH
FETCHING PRICE DATA FOR TICKER(S): XRP,BTC,XLM,ETH
🔹 $BTC: €101967.76566273384
🔹 $ETH: €2885.722839254806
🔹 $XLM: €0.3920890444361331
🔹 $XRP: €2.6160011996817576
```

Fetch the price of a cryptocurrency in a specific fiat currency

```bash
$ crypto-fetch price XRP --currency USD
FETCHING PRICE DATA FOR TICKER(S): XRP
🔹 $XRP: $3.0440291410769404 (USD)

# short-hand
$ crypto-fetch price XRP -c USD
FETCHING PRICE DATA FOR TICKER(S): XRP
🔹 $XRP: $3.0440291410769404 (USD)
```

### convert command

---

Convert a specified amount of a cryptocurrency (default fiat is EUR)

```bash
$ crypto-fetch convert 500 --ticker XRP
CONVERTING...
🔸 500.0 $XRP => €1308.5852403462009

# short-hand
$ crypto-fetch convert 500 -t XRP
CONVERTING...
🔸 500.0 $XRP => €1308.5852403462009
```

Convert a specified amount of a cryptocurrency to a specified fiat currency

```bash
$ crypto-fetch convert 500 --ticker XRP --currency USD
CONVERTING...
🔸 500.0 $XRP => $1522.8396407638309 (USD)

# short-hand
$ crypto-fetch convert 500 -t XRP -c USD
CONVERTING...
🔸 500.0 $XRP => $1522.8396407638309 (USD)
```

Convert a list of cryptocurrencies to a specified fiat currency

```bash
$ crypto-fetch convert -f portfolio.txt
# TODO Implement
```
