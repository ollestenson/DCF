from scripts.fetch_data import get_financial_data, check_ticker_data
from scripts.db_manager import init_db, insert_data, should_fetch_data, update_last_updated
from scripts.dcf_model import run_dcf
from scripts.config import TICKERS, GROWTH_RATE, DISCOUNT_RATE, TERMINAL_GROWTH, YEARS, DB_PATH, TEST_DB_PATH, REFRESH_DAYS

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# ----- Main -----
def main():
    """
    Main function to run the DCF analysis.
    This function initializes the database, fetches financial data, runs the DCF model,
    and plots the results.
    """

    #test()

    print(f"Starting DCF analysis at {datetime.now()}")

    engine = init_db(DB_PATH)

    # Fetches financial data if needed, else retrieves from database
    if should_fetch_data(engine, TICKERS ,'financial_data', REFRESH_DAYS):
        print("Fetching new data...")
        df = get_financial_data(TICKERS)                              # Fetch financial data for the tickers
        insert_data(engine, df, 'financial_data')           # Insert data into the financial_data table
        update_last_updated(engine, 'financial_data')       # Update last updated timestamp
    else:
        print("Data is up to date - fetching from database")
        df = pd.read_sql("SELECT * FROM financial_data", engine, index_col=["ticker", "year"])  # Read data from the financial_data table


    dcf_df, results_df = run_dcf(df, GROWTH_RATE, DISCOUNT_RATE, TERMINAL_GROWTH, YEARS)    # Run DCF analysis
    insert_data(engine, dcf_df, 'dcf_table')            # Insert DCF results into the dcf_table
    insert_data(engine, results_df, 'results_table')    # Insert results into the results_table

    plot_results(results_df)

def test():
    """
    Test function to verify program without running the full DCF analysis.
    """
    print("Running test function...")
    # Write test here
    print("Exiting test function...")
    exit()

def plot_results(df):
    """
    Plots the results of the DCF analysis.
    :param df: DataFrame containing the results with columns ['share_price', 'estimated_price', 'margin_of_safety']
    """
    plt.figure(figsize=(10,6))

    plt.plot(df.index, df["share_price"], marker="o", label="Share Price")
    plt.plot(df.index, df["estimated_price"], marker="s", label="Estimated Price")

    plt.bar(df.index, df["margin_of_safety"], alpha=0.3, label="Margin of Safety")

    plt.title("Stock Valuation Results")
    plt.xlabel("Ticker")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.show()

if __name__ == "__main__":
    main()