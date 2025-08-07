from datetime import datetime, timedelta
from scripts.config import FETCH_CONFIG

import yfinance as yf
import pandas as pd
import numpy as np

def check_ticker_data (ticker, category):
    stock = yf.Ticker(ticker)
    data = getattr(stock, category, pd.DataFrame())
    print(data)

def get_financial_data(tickers, config=None):

    if config is None:
        config = FETCH_CONFIG

    data = []


    for ticker in tickers:
        stock = yf.Ticker(ticker)

        category_cache = {}
        for category in config.keys():
            if category == 'info':
                category_cache['info'] = stock.info
            else:
                category_cache[category] = getattr(stock, category, pd.DataFrame())

        years_seen, fiscal_date_by_year = get_fiscal_dates_and_years(category_cache)

        if not years_seen:
            years_seen = {None}
        for year in years_seen:
            row = {'ticker':ticker, 'year': year}
            for category, fields in config.items():
                if category == 'info':
                    info = category_cache['info']
                    for yf_field, col_name in fields.items():
                        row[col_name] = info.get(yf_field)

                elif category == 'custom':
                    for field_key, col_name in fields.items():
                        if field_key == 'share_price' and year is not None:
                            fiscal_date = fiscal_date_by_year.get(year)
                            row[col_name] = get_price_on_fiscal_date(stock, fiscal_date)
                        else:
                            row[col_name] = None

                else:
                    df_cat = category_cache.get(category, pd.DataFrame())
                    if df_cat.empty:
                        for col_name in fields.values():
                            row[col_name] = None
                        continue
                    for yf_field, col_name in fields.items():
                        if yf_field in df_cat.index:
                            value = None
                            for col_date, val in df_cat.loc[yf_field].items():
                                if year == pd.to_datetime(col_date).year:
                                    value = val
                                    break
                            row[col_name] = value
                        else:
                            row[col_name] = None
            data.append(row)


    df = pd.DataFrame(data)
    df.set_index(['ticker', 'year'], inplace=True)
    df = df.sort_index(level=[0, 1], ascending=[True, False])
    print(df)
    return df


def get_price_on_fiscal_date(stock, fiscal_date):
    target_date = pd.to_datetime(fiscal_date).to_pydatetime()
    start = target_date - timedelta(days=5)
    end = target_date + timedelta(days=5)

    hist = stock.history(start=start, end=end)

    if hist.empty:
        return None

    hist.index = hist.index.tz_localize(None)  # remove timezone
    hist['diff'] = np.abs(hist.index - target_date)
    closest_row = hist.loc[hist['diff'].idxmin()]
    return closest_row['Close']

def get_fiscal_dates_and_years(category_cache, priority=("financials", "balancesheet", "cashflow")):
    '''
    :param category_cache:
    :param priority:
    :return:    set: years found in available data
                dict: {year: fiscal_date}
    '''

    fiscal_date_by_year = {}
    years_seen = set()

    for category in priority:
        df_cat = category_cache.get(category)
        if df_cat.empty:
            continue
        for col in df_cat.columns:
            col_date = pd.to_datetime(col, errors="coerce")
            if pd.isna(col_date):
                continue
            year = col_date.year
            if year not in fiscal_date_by_year:
                fiscal_date_by_year[year] = col_date
                years_seen.add(year)

    return years_seen, fiscal_date_by_year