from scripts.fetch_data import get_financial_data, check_ticker_data
from scripts.db_manager import init_db, insert_data, should_fetch_data, update_last_updated
from scripts.dcf_model import run_dcf
from scripts.config import TICKERS, GROWTH_RATE, DISCOUNT_RATE, TERMINAL_GROWTH, YEARS, DB_PATH, TEST_DB_PATH, REFRESH_DAYS

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# ----- Main -----
def main():

    #test()

    print(f"Starting DCF analysis at {datetime.now()}")

    engine = init_db(DB_PATH)

    if should_fetch_data(engine, TICKERS ,'financial_data', REFRESH_DAYS):
        print("Fetching new data...")
        df = get_financial_data(TICKERS)
        insert_data(engine, df, 'financial_data')
        update_last_updated(engine, 'financial_data')
    else:
        print("Data is up to date - fetching from database")
        df = pd.read_sql("SELECT * FROM financial_data", engine, index_col=["ticker", "year"])


    dcf_df, results_df = run_dcf(df, GROWTH_RATE, DISCOUNT_RATE, TERMINAL_GROWTH, YEARS)
    insert_data(engine, dcf_df, 'dcf_table')
    insert_data(engine, results_df, 'results_table')

    plot_results(results_df)

def test():
    """
    Test function to verify program without running the full DCF analysis.
    """
    print("Running test function...")
    #engine = init_db(TEST_DB_PATH)
    #df.to_csv(r"..\data\data.csv")
    #df = pd.read_csv(r"..\data\data.csv", index_col=['ticker', 'year'])
    #insert_data(engine, df, 'financial_data')
    #print("Test data fetched successfully.")
    #print(check_ticker_data('SAGA-B.ST', 'financials'))
    #dcf_df, prices = run_dcf(df, GROWTH_RATE, DISCOUNT_RATE, TERMINAL_GROWTH, YEARS)
    #insert_data(engine, dcf_df, 'dcf_results')
    #print(dcf_df)
    #print(prices)

    engine = init_db(TEST_DB_PATH)

    if should_fetch_data(engine, 'financial_data', REFRESH_DAYS):
        df = get_financial_data(TICKERS)
        insert_data(engine, df, 'financial_data')
        update_last_updated(engine, 'financial_data')
    else:
        print("Data is up to date - fetching from database")
        df = pd.read_sql("SELECT * FROM financial_data", engine, index_col=["ticker", "year"])

    print(df)

    print("Exiting test function...")
    exit()

def plot_results(df):
    plt.figure(figsize=(10,6))

    # plot actual vs estimated share prices
    plt.plot(df.index, df["share_price"], marker="o", label="Share Price")
    plt.plot(df.index, df["estimated_price"], marker="s", label="Estimated Price")

    # add margin of safety as bar chart (optional)
    plt.bar(df.index, df["margin_of_safety"], alpha=0.3, label="Margin of Safety")

    plt.title("Stock Valuation Results")
    plt.xlabel("Ticker")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.show()

if __name__ == "__main__":
    main()