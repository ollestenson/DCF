import yfinance as yf
import pandas as pd


def get_financial_data(tickers):

    df_dcf = get_fcf(tickers)
    df_shares = get_shares_outstanding(tickers)

    df = df_dcf.join(df_shares)
    df.index = df.index.set_levels(df.index.levels[1].year, level=1)
    return df


def get_fcf(tickers):
    """
    Fetch the Free Cash Flow (FCF) for a specific ticker.
    """
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            cash_flow = stock.cashflow.iloc[:,:-1]
            if not cash_flow.empty and 'Free Cash Flow' in cash_flow.index:
                fcf = cash_flow.loc['Free Cash Flow']
                for date, value in fcf.items():
                    data.append({'ticker': ticker, 'year': date, 'fcf': value})
            else:
                data.append({'ticker': ticker, 'year': None, 'fcf': None})
        except Exception as e:
            data.append({'ticker': ticker, 'year': None, 'fcf': None})
    df = pd.DataFrame(data)
    df.set_index(['ticker', 'year'], inplace=True)

    return df

def get_shares_outstanding(tickers):
    """
    Fetch the shares outstanding for a specific ticker.
    """
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            balance_sheet = stock.balancesheet.iloc[:, :-1]
            if not balance_sheet.empty and 'Ordinary Shares Number' in balance_sheet.index:
                shares = balance_sheet.loc['Ordinary Shares Number']
                for date, value in shares.items():
                    data.append({'ticker': ticker, 'year': date, 'shares': value})
            else:
                data.append({'ticker': ticker, 'year': None, 'shares': None})
        except Exception as e:
            data.append({'ticker': ticker, 'year': None, 'shares': None})
    df = pd.DataFrame(data)
    df.set_index(['ticker', 'year'], inplace=True)

    return df
