import numpy as np
import pandas as pd
from google.protobuf.text_format import PrintField
from pandas.core.interchange.from_dataframe import primitive_column_to_ndarray


def run_dcf(df, growth_rate, discount_rate, terminal_growth, years=5) -> (pd.DataFrame, float):
    print("Running DCF analysis...")
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
    print(share_price)
    return dcf_df, share_price

def wacc():
    return
