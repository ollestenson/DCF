import yfinance as yf
import pandas as pd

fields_to_fetch = {
    'cashflow': {
        'Free Cash Flow': 'fcf'
    },
    'balancesheet': {
        'Long Term Debt': 'long_term_debt',
        'Short Term Debt': 'short_term_debt'
    },
    'financials': {
        'Income Tax Expense': 'tax_expense',
        'Ebit': 'ebit',
        'Interest Expense': 'interest_expense'
    },
    'info': {
        #'sharesOutstanding': 'shares_outstanding',
        'impliedSharesOutstanding': 'shares_outstanding',
        'marketCap': 'market_cap',
        'beta': 'beta'
    }
}

def get_financial_data(tickers, fields=None):

    if fields is None:
        fields = fields_to_fetch

    ticker = tickers[0]

    data = []

    for ticker in tickers:
            stock = yf.Ticker(ticker)
            for field, subdicts in fields.items():
                if field == 'info':
                    info = stock.info
                    for subfield, alias in subdicts.items():
                        value = info.get(subfield, None)
                        data.append({'ticker': ticker, 'field': alias, 'value': value})
                else:
                    continue

    df = pd.DataFrame(data)
    #df.set_index(['ticker', 'year'], inplace=True)

    print(df)
    #df_dcf = get_fcf(tickers)
    #df_shares = get_shares_outstanding(tickers)

    #df = df_dcf.join(df_shares)
    #df.index = df.index.set_levels(df.index.levels[1].year, level=1)
    #return df


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

def get_share_price(tickers):
    """
    Fetch the share price for a specific ticker.
    """
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            earning_dates = stock.earnings_dates
            print(earning_dates)
            if not earning_dates.empty and 'Ordinary Shares Number' in earning_dates.index:
                share_price = earning_dates.loc['Ordinary Shares Number']
                for date, value in share_price.items():
                    data.append({'ticker': ticker, 'year': date, 'share_price': value})
            else:
                data.append({'ticker': ticker, 'year': None, 'share_price': None})
        except Exception as e:
            data.append({'ticker': ticker, 'year': None, 'share_price': None})
    df = pd.DataFrame(data)
    df.set_index(['ticker', 'year'], inplace=True)

    return df
