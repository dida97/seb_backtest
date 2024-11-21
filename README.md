```
seb_backtest/
├── data/
│   ├── sp500_tickers.txt
│   ├── sp500_sectors.txt
│   ├── daily_stocks.csv
│   ├── daily_index.csv
│   ├── stocks_intraday.csv
│   ├── index_intraday.csv
├── backtester/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── trading/
│   │   ├── __init__.py
│   │   ├── trading_algo.py
│   │   ├── strategies.py
│   │   ├── analysis.py
│   │   ├── execution.py
│   │   ├── utils.py
│   ├── data/
│   │   ├── downloader.py
│   │   ├── cleaner.py
│   │   ├── loader.py
├── tests/
│   ├── test_trading_algo.py
│   ├── test_data_loader.py
│   ├── test_strategies.py
├── requirements.txt
└── README.md
```

TODO: 
- upload sample data in data folder 