# List of tickers to analyze
#TICKERS = ['SAGA-B.ST', 'INVE-B.ST','VOLV-B.ST']
#TICKERS = ['BALD-B.ST','CORE-B.ST', 'SAGA-B.ST']
TICKERS = ['SAGA-B.ST', 'INVE-B.ST', 'VOLV-B.ST', 'BALD-B.ST', 'CORE-B.ST']
REFRESH_DAYS = 7

GROWTH_RATE = 0.05          # 5% annual growth
DISCOUNT_RATE = 0.10        # 10% discount rate (If not calculating WACC)
TERMINAL_GROWTH = 0.02      # 2% perpetual growth

# DCF variables
YEARS = 5
RISK_FREE_RETURN = 0.025
MARKET_RETURN = 0.08

# Database file location
DB_PATH = r"../db/dcf.db"
TEST_DB_PATH = r"../db/test_dcf.db"

# Fetches the config + share_price at fiscal date
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