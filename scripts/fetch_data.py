import yfinance as yf
import pandas as pd


def get_financial_data(tickers):
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            cash_flow = stock.cashflow
            if not cash_flow.empty and 'Free Cash Flow' in cash_flow.index:
                latest_date = cash_flow.columns[0]
                free_cash_flow = cash_flow.loc['Free Cash Flow', latest_date]
                data.append({'ticker': ticker, 'date': latest_date, 'free_cash_flow': free_cash_flow})
            else:
                data.append({'ticker': ticker, 'date': None, 'free_cash_flow': None})
        except Exception as e:
            data.append({'ticker': ticker, 'date': None, 'free_cash_flow': None})
    df = pd.DataFrame(data)

    df.index.names = ['date', 'ticker']

    df.columns = df.columns.str.lower()

    print(df)
    return df