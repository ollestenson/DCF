import numpy as np
import pandas as pd
from datetime import datetime
from scripts.config import RISK_FREE_RETURN, MARKET_RETURN

def run_dcf(df, growth_rate, discount_rate, terminal_growth, years) -> (pd.DataFrame, float):
    print("Running DCF model...")

    tickers = df.index.get_level_values('ticker').unique()

    all_dcf = []
    results = {}

    for ticker in tickers:
        ticker_df = df.loc[ticker]
        wacc = calculate_wacc(ticker_df, RISK_FREE_RETURN, MARKET_RETURN, discount_rate)
        ticker_dcf, share_price = calculate_dcf(ticker_df, growth_rate, wacc, terminal_growth, years)

        ticker_dcf.index = pd.MultiIndex.from_product([[ticker], ticker_dcf.index], names=["ticker", "year"])

        all_dcf.append(ticker_dcf)
        margin_of_safety =  ((share_price - ticker_df['share_price'].iloc[0]) / share_price) * 100
        results[ticker] = [datetime.now(), ticker_df['share_price'].iloc[0], share_price, margin_of_safety]

    print(results)
    results_df = pd.DataFrame.from_dict(results, orient="index", columns=["date", "share_price", "estimated_price", "margin_of_safety"])
    print(results_df)
    dcf_df = pd.concat(all_dcf)
    return dcf_df, results_df

def calculate_dcf(df, growth_rate, discount_rate, terminal_growth, years=5) -> (pd.DataFrame, float):
    start_year = df.index[0] + 1
    index = [start_year + i for i in range(years)]
    dcf_df = pd.DataFrame(index=index, columns=[ 'projected_fcf', 'discounted_fcf', 'projected_tv', 'discounted_tv'])
    dcf_df.index.name = 'year'

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

    wacc = (rdebt * (1-taxrate) * (debt / (equity+debt))) + (requity * (equity/(equity+debt)) )
    equity = market_cap
    debt = total_rebt
    rdebt = interest_expense / debt
    tax_rate = tax_rate
    requity = rf + beta * (rm - rf)  - CAPM
    '''
    equity = df.iloc[0]['market_cap']
    debt = df.iloc[0]['total_debt']
    rdebt = df.iloc[0]['interest_expense'] / debt
    tax_rate = df.iloc[0]['tax_rate']
    requity = rf + df.iloc[0]['beta'] * (rm -rf)
    wacc =  (rdebt * (1-tax_rate) * (debt / (equity+debt))) + (requity * (equity/(equity+debt)) )

    if wacc is None:
        print("WACC is none, falling back on default discount rate")
        return default_discount_rate

    # Set WACC floor to 0.08
    wacc = wacc if wacc >= 0.08 else 0.08

    return wacc
