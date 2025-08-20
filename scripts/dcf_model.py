import numpy as np
import pandas as pd
from datetime import datetime
from scripts.config import RISK_FREE_RETURN, MARKET_RETURN

def run_dcf(df, growth_rate, discount_rate, terminal_growth, years):
    """
    Runs the DCF model on the provided financial data.
    :param df: DataFrame containing financial data with columns ['fcf', 'total_debt', 'tax_rate', 'interest_expense', 'shares_outstanding', 'market_cap', 'beta', 'share_price']
    :param growth_rate: Annual growth rate for projected free cash flows
    :param discount_rate: Discount rate for DCF calculations
    :param terminal_growth: Terminal growth rate for calculating terminal value
    :param years: Number of years to project free cash flows
    :return: DataFrame with DCF results and a summary DataFrame with estimated prices and margin of safety
    """
    print("Running DCF model...")

    tickers = df.index.get_level_values('ticker').unique()  # Get unique tickers from the DataFrame index

    all_dcf = []    # List to store DCF calculations for each ticker
    results = {}    # Dictionary to store results for each ticker

    for ticker in tickers:
        ticker_df = df.loc[ticker]
        wacc = calculate_wacc(ticker_df, RISK_FREE_RETURN, MARKET_RETURN, discount_rate)
        ticker_dcf, share_price = calculate_dcf(ticker_df, growth_rate, wacc, terminal_growth, years)   # Calculate DCF for the ticker

        ticker_dcf.index = pd.MultiIndex.from_product([[ticker], ticker_dcf.index], names=["ticker", "year"])   # Set MultiIndex for DCF DataFrame

        all_dcf.append(ticker_dcf)  # Append DCF calculation DataFrame to the list
        margin_of_safety =  ((share_price - ticker_df['share_price'].iloc[0]) / share_price) * 100
        results[ticker] = [datetime.now(), ticker_df['share_price'].iloc[0], share_price, margin_of_safety]


    results_df = pd.DataFrame.from_dict(results, orient="index", columns=["date", "share_price", "estimated_price", "margin_of_safety"])
    dcf_df = pd.concat(all_dcf)
    return dcf_df, results_df

def calculate_dcf(df, growth_rate, discount_rate, terminal_growth, years=5) -> (pd.DataFrame, float):
    """
    Calculates the DCF model for a given DataFrame of financial data for a specific ticker.
    :param df:
    :param growth_rate:
    :param discount_rate:
    :param terminal_growth:
    :param years:
    :return: A DataFrame with DCF calculations and the estimated share price
    """
    start_year = df.index[0] + 1    # Start from the next year after the last year in the DataFrame
    index = [start_year + i for i in range(years)]  # Create an index for the projected years
    dcf_df = pd.DataFrame(index=index, columns=[ 'projected_fcf', 'discounted_fcf', 'projected_tv', 'discounted_tv'])   # Initialize DCF DataFrame with the projected years as index
    dcf_df.index.name = 'year'  # Set the index name to 'year'

    # Calculate Projected Free Cash Flows (FCF)
    initial_fcf = df.iloc[0]['fcf']
    dcf_df['projected_fcf'] = [initial_fcf * (1 + growth_rate)**i for i in range(1, years + 1)]
    # Calculate Discounted Free Cash Flows (DCF)
    dcf_df['discounted_fcf'] = [projected_fcf / (1 + discount_rate)**i for i, projected_fcf in enumerate(dcf_df['projected_fcf'], start=1)]
    # Calculate Terminal Value (TV)
    terminal_value = dcf_df['projected_fcf'].iloc[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    dcf_df.loc[dcf_df.index[-1], 'projected_tv'] = terminal_value
    # Calculate Discounted Terminal Value (DTV)
    dcf_df.loc[dcf_df.index[-1], 'discounted_tv'] = terminal_value / ((1 + discount_rate) ** years)
    # Calculate Total DCF and Share Price
    total_dcf = dcf_df['discounted_fcf'].sum() + dcf_df.iloc[-1]['discounted_tv']
    share_price = total_dcf / df.iloc[0]['shares_outstanding']

    return dcf_df, share_price

# TODO: - Improve WACC calculations
def calculate_wacc(df, rf, rm, default_discount_rate):
    '''
    Calculates WACC and returns df with new column wacc.
    :param df: DataFrame containing financial data with columns ['market_cap', 'total_debt', 'interest_expense', 'tax_rate', 'beta']
    :param rf: Risk-free rate
    :param rm: Market return
    :param default_discount_rate: Default discount rate to use if WACC cannot be calculated or is too low
    :return: WACC value

    Formula:
    wacc = (rdebt * (1-taxrate) * (debt / (equity+debt))) + (requity * (equity/(equity+debt)) )
    equity = market_cap
    debt = total_rebt
    rdebt = interest_expense / debt
    tax_rate = tax_rate
    requity = rf + beta * (rm - rf)  - CAPM formula for required return on equity
    '''

    # Perform calculations for WACC
    equity = df.iloc[0]['market_cap']
    debt = df.iloc[0]['total_debt']
    rdebt = df.iloc[0]['interest_expense'] / debt
    tax_rate = df.iloc[0]['tax_rate']
    requity = rf + df.iloc[0]['beta'] * (rm -rf)
    wacc =  (rdebt * (1-tax_rate) * (debt / (equity+debt))) + (requity * (equity/(equity+debt)) )

    # Check if WACC is None or below the default discount rate
    if wacc is None:
        print("WACC is none, falling back on default discount rate")
        return default_discount_rate

    # Set WACC floor to 0.08
    wacc = wacc if wacc >= 0.08 else 0.08

    return wacc
