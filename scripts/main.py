from scripts.fetch_data import get_financial_data

import pandas as pd
from datetime import datetime

# List of tickers to analyze
TICKERS = ['BALD-B.ST','SAGA-B.ST', 'CORE-B.ST', 'SBB-B.ST']

# DCF Assumptions

# Database file location


# ----- Main -----
def main():
    df = get_financial_data(TICKERS)
    print(df)


if __name__ == "__main__":
    main()