from scripts.fetch_data import get_financial_data, check_ticker_data
from scripts.db_manager import init_db, insert_data, should_fetch_data, update_last_updated, upsert_data
from scripts.dcf_model import run_dcf
from scripts.config import TICKERS, GROWTH_RATE, DISCOUNT_RATE, TERMINAL_GROWTH, YEARS, DB_PATH, TEST_DB_PATH, REFRESH_DAYS

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
        #insert_data(engine, df, 'financial_data')
        upsert_data(engine, df, 'financial_data', ['ticker', 'year'])  # Upsert financial data into the financial_data table
        update_last_updated(engine, 'financial_data')       # Update last updated timestamp
    else:
        print("Data is up to date - fetching from database")
        placeholders = ', '.join(['?'] * len(TICKERS))  # Create placeholders for the SQL query
        sql = f"SELECT * FROM financial_data WHERE ticker IN ({placeholders}) ORDER BY ticker ASC, year DESC"   # SQL query to select financial data for the specified tickers
        df = pd.read_sql(sql, engine, params=tuple(TICKERS), index_col=["ticker", "year"])  # Read data from the financial_data table

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
    x = np.arange(len(df.index))  # Numerical positions for tickers
    width = 0.35

    plt.figure(figsize=(12, 6))
    plt.bar(x - width / 2, df["share_price"], width, label="Share Price")
    plt.bar(x + width / 2, df["estimated_price"], width, label="Estimated Price")

    # Annotate Share Price bars
    for i, v in enumerate(df["share_price"]):
        plt.text(i - width / 2, v + 1, f"{v:.1f} SEK", ha="center", va="bottom", fontsize=8)

    # Annotate Estimated Price bars
    for i, v in enumerate(df["estimated_price"]):
        plt.text(i + width / 2, v + 1, f"{v:.1f} SEK", ha="center", va="bottom", fontsize=8)

    # Optional: add margin of safety as text above bars
    for i, v in enumerate(df["margin_of_safety"]):
        plt.text(i, max(df["share_price"].iloc[i], df["estimated_price"].iloc[i]) + 12,
                 f"{v:.1f}%", ha="center", va="bottom")

    ymax = max(df["share_price"].max(), df["estimated_price"].max())
    plt.ylim(0, ymax * 1.1)  # 10% padding

    plt.xticks(x, df.index, rotation=45, ha="right")
    plt.ylabel("Price")
    plt.title("DCF vs Market Price by Ticker")
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()