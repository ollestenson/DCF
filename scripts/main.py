from scripts.fetch_data import get_financial_data

import pandas as pd
from datetime import datetime

# List of tickers to analyze
TICKERS = ['BALD-B.ST']

# DCF Assumptions

# Database file location


# ----- Main -----
def main():
    get_financial_data(TICKERS)



if __name__ == "__main__":
    main()