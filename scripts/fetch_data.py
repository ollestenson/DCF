from datetime import datetime, timedelta
from scripts.config import FETCH_CONFIG

import yfinance as yf
import pandas as pd
import numpy as np


def get_financial_data(tickers, config=None):
    """
    Fetches financial data for the given tickers using yfinance and returns a DataFrame.
    :param tickers: List of ticker symbols to fetch data for (e.g., ['AAPL', 'GOOGL']).
    :param config: Configuration dictionary defining the fields to fetch for each category.
    :return: DataFrame with financial data indexed by ticker then year.
    """
    if config is None:
        config = FETCH_CONFIG   # Default configuration from config.py

    data = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)   # Fetch the stock data using yfinance

        category_cache = {}  # Cache to store fetched data for each category
        for category in config.keys():  # Iterate through each category in the config
            if category == 'info':  # Special case for 'info' category (not time series data)
                category_cache['info'] = stock.info
            else:
                category_cache[category] = getattr(stock, category, pd.DataFrame())

        # Get fiscal dates and years from the fetched data
        years_seen, fiscal_date_by_year = get_fiscal_dates_and_years(category_cache)

        if not years_seen:  # If no years were found, skip this ticker
            years_seen = {None}
        for year in years_seen: # Iterate through each year found in the data
            row = {'ticker':ticker, 'year': year}   # Initialize a row with ticker and year
            for category, fields in config.items(): # Iterate through each category and its fields
                if category == 'info':  # Special case for 'info' category
                    info = category_cache['info']
                    for yf_field, col_name in fields.items():   # Iterate through each field in the 'info' category
                        row[col_name] = info.get(yf_field)  # If the field exists in the info dictionary, assign its value to the row

                elif category == 'custom':  # Custom fields that are not fetched directly from yfinance
                    for field_key, col_name in fields.items():  # Iterate through each custom field
                        if field_key == 'share_price' and year is not None: # Fetch share price on fiscal date
                            fiscal_date = fiscal_date_by_year.get(year)
                            row[col_name] = get_price_on_fiscal_date(stock, fiscal_date)
                        else:
                            row[col_name] = None

                else:   # For the rest of the categories (financials, balancesheet, cashflow)
                    df_cat = category_cache.get(category, pd.DataFrame())   # If the category data is not found, use an empty DataFrame
                    if df_cat.empty:    # If the category DataFrame is empty, set all fields to None
                        for col_name in fields.values():
                            row[col_name] = None
                        continue
                    for yf_field, col_name in fields.items():   # Iterate through each field in the category
                        if yf_field in df_cat.index:    # If the field exists in the DataFrame index
                            value = None    # Initialize value to None
                            for col_date, val in df_cat.loc[yf_field].items(): # Iterate through each column in the DataFrame
                                if year == pd.to_datetime(col_date).year:   # Check if the year matches the column date
                                    value = val # Assign the value if the year matches
                                    break
                            row[col_name] = value   # If a value was found, assign it to the row
                        else:
                            row[col_name] = None
            data.append(row)    # Append the row to the data list


    df = pd.DataFrame(data) # Create a DataFrame from the list of rows
    df.set_index(['ticker', 'year'], inplace=True)  # Set the index to be a MultiIndex with ticker and year
    df = df.sort_index(level=[0, 1], ascending=[True, False])   # Sort the DataFrame by ticker and year in descending order
    return df


def get_price_on_fiscal_date(stock, fiscal_date):
    """
    Fetches the stock price on the fiscal date, looking 5 days before and after the fiscal date.
    :param stock: yfinance Ticker object for the stock.
    :param fiscal_date: The fiscal date to fetch the stock price for (as a string or datetime).
    :return: The closing stock price on the fiscal date, or None if no data is available.
    """
    target_date = pd.to_datetime(fiscal_date).to_pydatetime()   # Convert fiscal date to a datetime object
    start = target_date - timedelta(days=5)
    end = target_date + timedelta(days=5)

    hist = stock.history(start=start, end=end)

    if hist.empty:  # If no historical data is available, return None
        return None

    hist.index = hist.index.tz_localize(None)  # Remove timezone information from the index
    hist['diff'] = np.abs(hist.index - target_date) # Calculate the absolute difference between each date in the index and the target date
    closest_row = hist.loc[hist['diff'].idxmin()]   # Find the row with the minimum difference (closest date to the target date)
    return closest_row['Close']

def get_fiscal_dates_and_years(category_cache, priority=("financials", "balancesheet", "cashflow")):
    """
    Extracts fiscal dates and years from the category cache based on the specified priority.
    :param category_cache: Dictionary containing DataFrames for each financial category.
    :param priority: Tuple of category names in order of priority to check for fiscal dates.
    :return: Tuple containing:
        - Set of years seen in the fiscal data.
        - Dictionary mapping years to their corresponding fiscal date.
    """
    fiscal_date_by_year = {}    # Dictionary to store fiscal dates by year
    years_seen = set()

    for category in priority:
        df_cat = category_cache.get(category)
        if df_cat.empty:    # If the category DataFrame is empty, skip to the next category
            continue
        for col in df_cat.columns:  # Iterate through each column in the category DataFrame
            col_date = pd.to_datetime(col, errors="coerce") # Convert the column name to a datetime object, coercing errors to NaT
            if pd.isna(col_date):   # If the column date is NaT (not a valid date), skip to the next column
                continue
            year = col_date.year    # Extract the year from the column date
            if year not in fiscal_date_by_year: # If the year is not already in the fiscal_date_by_year dictionary
                fiscal_date_by_year[year] = col_date    # Assign the column date to the year in the dictionary
                years_seen.add(year) # Add the year to the set of years seen

    return years_seen, fiscal_date_by_year

def check_ticker_data (ticker, category):
    """
    Fetches and prints the specified financial data category for a given ticker using yfinance.
    :param ticker: Ticker symbol of the stock (e.g., 'AAPL', 'GOOGL').
    :param category: E.g. ('cashflow', 'balancesheet', 'financials', 'info').
    :return: None
    """
    stock = yf.Ticker(ticker)
    data = getattr(stock, category, pd.DataFrame())
    print(data)
    return