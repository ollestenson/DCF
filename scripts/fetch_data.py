import yfinance as yf
import pandas as pd


def get_financial_data(tickers):
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            cash_flow = stock.cashflow.iloc[:,:-1]
            if not cash_flow.empty and 'Free Cash Flow' in cash_flow.index:
                fcf = cash_flow.loc['Free Cash Flow']
                for date, value in fcf.items():
                    data.append({'ticker': ticker, 'date': date, 'fcf': value})
            else:
                data.append({'ticker': ticker, 'date': None, 'fcf': None})
        except Exception as e:
            data.append({'ticker': ticker, 'date': None, 'fcf': None})
    df = pd.DataFrame(data)
    df.set_index(['ticker', 'date'], inplace=True)

    return df