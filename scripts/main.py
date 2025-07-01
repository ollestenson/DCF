from scripts.fetch_data import get_financial_data

import pandas as pd
from datetime import datetime

# List of tickers to analyze
TICKERS = ['BALD-B.ST','SAGA-B.ST', 'CORE-B.ST', 'SBB-B.ST']

# DCF Assumptions (For simplicity, these are hardcoded)
GROWTH_RATE = 0.05          # 5% annual growth
DISCOUNT_RATE = 0.10        # 10% discount rate (WACC - Weighted Average Cost of Capital)
TERMINAL_GROWTH = 0.02      # 2% perpetual growth

# Database file location
DB_PATH = 'db/dcf.db'

# ----- Main -----
def main():
    print(f"Starting DCF analysis at {datetime.now()}")

    # init_db(DB_PATH)  # Initialize the database (if needed)
    df = get_financial_data(TICKERS)

    # dcf_df = run_dcf(df, GROWTH_RATE, DISCOUNT_RATE, TERMINAL_GROWTH, shares_outstanding=amount of company shares (get from fetch_data.py?))

    # insert_data(dcf_df, db)  # Insert data into the database
    print(df)


if __name__ == "__main__":
    main()