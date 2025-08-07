from scripts.fetch_data import get_financial_data, check_ticker_data
from scripts.db_manager import init_db, insert_data
from scripts.dcf_model import run_dcf
from scripts.config import TICKERS, TICKER, GROWTH_RATE, DISCOUNT_RATE, TERMINAL_GROWTH, YEARS, DB_PATH

from datetime import datetime
import pandas as pd

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
    #df = get_financial_data(TICKERS)
    #df.to_csv(r"..\data\data.csv")
    df = pd.read_csv(r"..\data\data.csv", index_col=['ticker', 'year'])
    #print("Test data fetched successfully.")
    #print(check_ticker_data('SAGA-B.ST', 'financials'))
    dcf_df, prices = run_dcf(df, GROWTH_RATE, DISCOUNT_RATE, TERMINAL_GROWTH, YEARS)
    print(dcf_df)
    print(prices)

    print("Exiting test function...")
    exit()

if __name__ == "__main__":
    main()