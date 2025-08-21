from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData, DateTime, text, inspect, select
from sqlalchemy.dialects.sqlite import insert
from datetime import datetime, timezone, timedelta
import pandas as pd

def init_db(db_path):
    """
    Initialize the database connection and create necessary tables.
    :param db_path: Path to the SQLite database file
    :return: SQLAlchemy engine object
    """
    print("Initializing database...")

    engine = create_engine(f"sqlite:///{db_path}")  # SQLite database connection
    metadata = MetaData()   # Metadata object to hold table definitions

    # Table 1: Financial Data
    financial_data = Table(
        "financial_data",
        metadata,
        Column("ticker", String, primary_key=True),
        Column("year", Integer, primary_key=True),
        Column("fcf", Float),
        Column("total_debt", Float),
        Column("tax_rate", Float),
        Column("interest_expense", Float),
        Column("shares_outstanding", Float),
        Column("market_cap", Float),
        Column("beta", Float),
        Column("share_price", Float),
    )

    # Table 2: DCF
    dcf_table = Table(
        "dcf_table",
        metadata,
        Column("ticker", String, primary_key=True),
        Column("year", Integer, primary_key=True),
        Column("projected_fcf", Float),
        Column("discounted_fcf", Float),
        Column("projected_tv", Float),
        Column("discounted_tv", Float),
    )

    # Table 3: Results
    results_table = Table(
        "results_table",
        metadata,
        Column("ticker", String, primary_key=True),
        Column("date", DateTime),
        Column("share_price", Float),
        Column("estimated_price", Float),
        Column("margin_of_safety", Float)
    )

    # Metadata table
    data_status = Table(
        "data_status",
        metadata,
        Column("table_name", String, primary_key=True),
        Column("last_updated", DateTime)
    )

    metadata.create_all(engine)

    return engine

# TODO: - Add error handling for database operations
def insert_data(engine, df, table_name):
    """
    Insert data into the database table.
    :param engine: SQLAlchemy engine object
    :param df: DataFrame containing the data to insert
    :param table_name: Name of the table to insert data into
    :return: None
    """
    print(f"inserting data in table: {table_name}")
    df.to_sql(name=table_name, con=engine, if_exists='replace', index=True)   # Replace existing table with new data
    return

def upsert_data(engine, df, table_name, keys):
    """
    Upsert data into the database table, updating existing rows based on specified keys.
    :param engine: SQLAlchemy engine object
    :param df: DataFrame containing the data to upsert
    :param table_name: Name of the table to upsert data into
    :param keys: List of column names to use as keys for upserting
    :return:
    """
    metadata = MetaData()  # Metadata object to hold table definitions
    table = Table(table_name, metadata, autoload_with=engine)  # Load the table definition from the database

    df = df.reset_index()  # Reset index to ensure 'ticker' and 'year' are columns
    rows = df.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries for insertion
    stmt = insert(table).values(rows)   # Create an insert statement with the rows to be inserted
    update_dict = {c.key: c for c in stmt.excluded if c.key not in keys}    # Create a dictionary of columns to update if a conflict occurs
    stmt = stmt.on_conflict_do_update(index_elements=keys, set_=update_dict)    # Handle conflicts by updating existing rows based on the specified keys

    with engine.begin() as conn:
        conn.execute(stmt)  # Execute the upsert statement within a transaction
    return

# TODO: - Add error handling for database operations
def get_last_updated(engine, table_name):
    """    Retrieve the last updated timestamp for a specific table.
    :param engine: SQLAlchemy engine object
    :param table_name: Name of the table to check
    :return: Last updated timestamp as a datetime object, or None if not found
    """
    with engine.connect() as conn:  # Establish a connection to the database
        sql = text("SELECT last_updated FROM data_status WHERE table_name = :name") # Parameterized SQL query to prevent SQL injection
        row = conn.execute(sql, {"name":table_name}).fetchone() # Fetch the first row of the result set
        if row is None:     # No rows returned
            return None
        if row[0] is None:  # If last_updated is None, return None
            return None
        last_updated = row[0]   # Extract the last_updated value from the row
        return last_updated if isinstance(last_updated, datetime) else datetime.fromisoformat(last_updated)


# TODO: - Add error handling for database operations
def update_last_updated(engine, table_name):
    """
    Update the last updated timestamp for a specific table in the database.
    :param engine: SQLAlchemy engine object
    :param table_name: Name of the table to update
    :return: None
    """
    print("Updating last_updated")
    now_utc = datetime.now(timezone.utc)    # Get the current UTC time
    sql = text("""INSERT INTO data_status (table_name, last_updated) 
                  VALUES (:name, :updated) ON CONFLICT (table_name) 
                  DO UPDATE SET last_updated = :updated""") # Upsert SQL query to insert or update the last_updated timestamp
    with engine.begin() as conn:    # Begin a transaction
         conn.execute(sql, {"name": table_name, "updated": now_utc})    # Execute the SQL query with parameters
    return

# TODO: - Add error handling for database operations
def should_fetch_data(engine, tickers, table_name, max_days):
    """
    Determines whether to fetch new data based on existing tickers and last updated timestamp.
    :param engine: SQLAlchemy engine object
    :param tickers: List of tickers to check against existing data
    :param table_name: Name of the table to check for existing data
    :param max_days: Maximum number of days since last update to consider fetching new data
    :return: True if new data should be fetched, False otherwise
    """
    existing_tickers = get_column_values(engine, table_name, "ticker")  # Get existing tickers from the specified table
    for ticker in tickers:
        if not ticker in existing_tickers:
            return True
    last = get_last_updated(engine, table_name)
    if last is None or pd.isna(last):   # If last updated is None or NaT, fetch new data
        return True
    if last.tzinfo is None:  # If last updated timestamp is naive (no timezone info), assume it's in UTC
        last = last.replace(tzinfo=timezone.utc)    # Convert to UTC timezone
    return datetime.now(timezone.utc) - last > timedelta(days=max_days)

def get_column_values(engine, table_name, column_name):
    """
    Returns a list of all values in a specific column.
    :param engine: SQLAlchemy engine object
    :param table_name: Name of the table to query
    :param column_name: Name of the column to retrieve values from
    :return: List of values in the specified column
    """
    metadata = MetaData()   # Metadata object to hold table definitions
    table = Table(table_name, metadata, autoload_with=engine)   # Load the table definition from the database

    with engine.connect() as conn:  # Establish a connection to the database
        stmt = select(getattr(table.c, column_name))    # Create a select statement to retrieve the specified column
        results = conn.execute(stmt).fetchall()     # Execute the statement and fetch all results
        return [r[0] for r in results]  # Convert results to a list of values

