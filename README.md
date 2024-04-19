# Sum trades from Kraken ledger file #

## Description ##

This script parses a ledger (transaction list) file from the cryptocurrency exchange [Kraken](http://www.kraken.com/). It sums all deposits, withdrawals, transfers (airdrops) and trades by asset (currency). In addition, it sums all trades sorted by buy-sell asset pairs.

The sorted trade sums can be used for tax purposes. Please note, however, that there is no filtering by calendar or fiscal year.

## Usage ##

Optimized for [Python 3.9](https://docs.python.org/release/3.9.19/).

```
usage: cli.py [-h] [--ledgers LEDGERS] [--trades TRADES]

Parse Kraken ledgers file. See https://tinyurl.com/kraken-ledgers for more details.

optional arguments:
  -h, --help         show this help message and exit
  --ledgers LEDGERS
  --trades TRADES
```

## Example input ##

### ledgers.csv ###

```csv
"txid","refid","time","type","subtype","aclass","asset","wallet","amount","fee","balance"
"LMEUII-4CF32-WGJ2TD","QCCGI4C-2C6N3X-CV2ZNN","2018-01-09 17:09:10","deposit","","currency","ZEUR","spot / main",200.0000,0,200.0000
"LPGWHB-JOQDA-AFUGP4","T4CEZL-KFN6U-NUFCE7","2018-01-09 18:01:56","trade","","currency","XXBT","spot / main",0.0020000000,0,0.0020000000
"LTMQ2A-PS5ZV-V63KW5","T4CEZL-KFN6U-NUFCE7","2018-01-09 18:01:56","trade","","currency","ZEUR","spot / main",-25.2800,-0.0657,174.6543
```

## Example output ##

This is an example output with arbitrary values. There, the trades totals don’t match the deposits, withdrawals etc. totals. The numbers in a real output would match.

### Plain text standard output ###

```
Total deposit:
ZEUR: 1940.0000, fee: 0
USDT: 395.64000000, fee: 0

Total buy:
XXBT: 0.2747138100, fee: 0.0005334700
USDT: 20.31553398, fee: 0.02063107
ZEUR: 3388.6500, fee: 50.0800

Total sell:
ZEUR: 1935.1585, fee: 4.8409
USDT: 1.88150000, fee: 0
XXBT: 0.0972093400, fee: 0

Total withdrawal:
XXBT: 0.1739710000, fee: 0.0030000000
USDT: 404.05334800, fee: 10.00000000
ZEUR: 3337.6700, fee: 0.9000

Total transfer:
SGB: 12.2919850000, fee: 0
ETHW: 0.2076400, fee: 0
FLR: 12.2915, fee: 0

Total trade:
XXBT for ZEUR: 0.2373036000, fee: 0 for 1343.4081, fee: 3.3328
USDT for ZEUR: 20.31553398, fee: 0.02063107 for 19.3800, fee: 0.0201
ZEUR for USDT: 1.7800, fee: 0.0300 for 1.88150000, fee: 0
ZEUR for XXBT: 3386.8700, fee: 50.0500 for 0.0972093400, fee: 0
```

### trades.csv ###

```csv
buy_asset,buy_amount,buy_fee,sell_asset,sell_amount,sell_fee
XXBT,0.2373036000,0,ZEUR,1343.4081,3.3328
ZEUR,1.7800,0.0300,USDT,1.88150000,0
ZEUR,3386.8700,50.0500,XXBT,0.0972093400,0
```

## Limitations ##

I only used this one-shot for a single ledgers file with all crypto → fiat withdrawals in a single year. Also, only a subset of the possible transaction types may have been present in my file. 

- **No filtering by calendar or fiscal year.**
- No filtering by asset.
- No CSV output for plain totals, only for trades by asset.
- Possibly unsupported transaction types.

**⚠️ Use at your own risk. I don’t guarantee correctness of the output and take no responsibility for any consequences resulting from its usage.**

## Reference ##

See Kraken’s article [How to interpret Ledger history fields](https://support.kraken.com/hc/en-us/articles/360001169383-How-to-interpret-Ledger-history-fields) to learn more about the ledger file.

## License ##

© 2024 Štěpán Tomsa / [Glutexo](https://github.com/Glutexo)

[MIT License](LICENSE.txt)