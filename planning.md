
##### Goal: 
- Create a simple DCF in Python and SQL.

##### Learning outcome:  
- Get more comfortable with Python/SQL and associated libraries.
- Get familiar with discounted cash flow analysis.

### Project Plan Step-for-step
1. Define project scope (Initial MVP)
   - List of tickers (manual or from an index)
   - Fetch financial data (yfinance)
   - Build simple DCF caluclations (with assumptions for growth & discount)
   - Store results into a SQL database (SQLite)
   - Query and review outputs

2. Decide tools
    - Python stack: pandas, numpy, sqlalchemy, yfinance
    - SQL: sqlite (for simplicity)

3. Start small:
   1. Get the DCF calculations to work for one ticker that is fetched with yfinance.
   2. Incorporate SQL 
   3. Scale up.