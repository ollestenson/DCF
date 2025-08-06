from scripts.fetch_data import get_financial_data
from scripts.db_manager import init_db, insert_data
from scripts.dcf_model import run_dcf

import pandas as pd
from datetime import datetime

# List of tickers to analyze
TICKERS = ['BALD-B.ST','SAGA-B.ST', 'CORE-B.ST', 'SBB-B.ST']
TICKER = 'BALD-B.ST'  # Example ticker

# DCF Assumptions (For simplicity, these are hardcoded)
GROWTH_RATE = 0.05          # 5% annual growth
DISCOUNT_RATE = 0.10        # 10% discount rate (WACC - Weighted Average Cost of Capital)
TERMINAL_GROWTH = 0.02      # 2% perpetual growth

# Database file location
DB_PATH = 'db/dcf.db'

# ----- Main -----
def main():

    test()

    print(f"Starting DCF analysis at {datetime.now()}")

    # init_db(DB_PATH)  # Initialize the database (if needed)
    df = get_financial_data(TICKERS)
    print("Financial data fetched successfully.")
    #print(df)

    print("processing DCF for ticker:", TICKER)
    dcf_df, share_price = run_dcf(df.loc[TICKER], GROWTH_RATE, DISCOUNT_RATE, TERMINAL_GROWTH)
    print(dcf_df)
    print(share_price)
    # insert_data(dcf_df, db)  # Insert data into the database


def test():
    """
    Test function to verify program without running the full DCF analysis.
    """
    print("Running test function...")
    df = get_financial_data(TICKERS)
    print("Test data fetched successfully.")
    print(df)

    print("Exiting test function...")
    exit()

if __name__ == "__main__":
    main()