"""
Configuration file for the DCF analysis script.
This file contains constants and configurations used throughout the script.
"""

TICKERS = ['BALD-B.ST', 'CORE-B.ST', 'SAGA-B.ST', 'CAST.ST']    # List of tickers to analyze
REFRESH_DAYS = 7    # Number of days to refresh data

GROWTH_RATE = 0.05          # 5% annual growth rate for projected free cash flows
DISCOUNT_RATE = 0.10        # 10% discount rate for DCF calculations (if not using WACC)
TERMINAL_GROWTH = 0.02      # 2% terminal growth rate for calculating terminal value

YEARS = 5   # Number of years to project free cash flows
RISK_FREE_RETURN = 0.025    # 2.5% risk-free return (e.g., from government bonds)
MARKET_RETURN = 0.08    # 8% expected market return (e.g., from stock market index)

# Database file location
DB_PATH = r"../db/dcf.db"    # Main database file for DCF analysis
TEST_DB_PATH = r"../db/test_dcf.db"     # Test database file for DCF analysis

# Configuration for fetching financial data from yfinance
FETCH_CONFIG = {
    'cashflow': {
        'Free Cash Flow': 'fcf'
    },
    'balancesheet': {
        'Net Debt': 'total_debt',
    },
    'financials': {
        'Tax Rate For Calcs': 'tax_rate',
        'Interest Expense': 'interest_expense'
    },
    'info': {
        #'sharesOutstanding': 'shares_outstanding',
        'impliedSharesOutstanding': 'shares_outstanding',
        'marketCap': 'market_cap',
        'beta': 'beta'
    },
    'custom': {
        'share_price': 'share_price'
    }
}