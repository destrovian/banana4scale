import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from matplotlib import pyplot as plt

# List of stock tickers for different markets
stock_tickers = {
    "US": ["AAPL", "MSFT", "GOOGL"],       # Example US stocks
    "EU": ["VOW3.DE", "AIR.PA", "BMW.DE"], # Example European stocks (Germany and France)
    "CH": ["NESN.SW", "NOVN.SW", "ROG.SW"] # Example Swiss stocks
}

# Function to fetch stock data for a given ticker
def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    hist_data = stock.history(start=start_date, end=end_date)
    return hist_data

if __name__ == "__main__":
    # Define date range: last 30 days
    today = datetime.now()
    start_date = '2000-01-01'
    end_date = today.strftime('%Y-%m-%d')

    # Fetch data for each ticker and save to CSV
    for market, tickers in stock_tickers.items():
        for ticker in tickers:
            try:
                print(f"Fetching data for {ticker}...")
                data = fetch_stock_data(ticker, start_date, end_date)
                if not data.empty:
                    data.to_csv(f'data/{ticker}_data.csv')
                    plt.plot(data['Data'], data['Close'])
                    plt.show()
                    print(f"Data for {ticker} saved successfully.")
                else:
                    print(f"No data found for {ticker}.")
            except Exception as e:
                print(f"Failed to fetch data for {ticker}: {e}")
