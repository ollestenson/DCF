import numpy as np
import pandas as pd

def run_dcf(df, growth_rate, discount_rate, terminal_growth, years=5) -> (pd.DataFrame, float):
    print("Running DCF analysis...")
    for ticker in df.index.get_level_values('ticker').unique():
        print(f"Processing ticker: {ticker}")
        most_recent_fcf = df.loc[ticker].iloc[0]['fcf']
        for n in range(1, years + 1):
            return
