from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData, DateTime, text
from datetime import datetime, timezone, timedelta
import pandas as pd

def init_db(db_path):
    """
    Initialize the database connection and create necessary tables.
    """
    print("Initializing database...")

    engine = create_engine(f"sqlite:///{db_path}")
    metadata = MetaData()

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
        "dcf_results",
        metadata,
        Column("ticker", String, primary_key=True),
        Column("year", Integer, primary_key=True),
        Column("projected_fcf", Float),
        Column("discounted_fcf", Float),
        Column("projected_tv", Float),
        Column("discounted_tv", Float),
    )

    # Table 3: Results
    prices = Table(
        "prices",
        metadata,
        Column("ticker", String, primary_key=True),
        Column("date", String),
        Column("share_price", Float),
        Column("estimated_price", Float)
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

def insert_data(engine, df, table_name):
    """
    Insert data into the database table.
    """
    print(f"inserting data in table: {table_name}")
    df.to_sql(name=table_name, con=engine, if_exists='replace', index=True)
    # Here you would implement the actual database insertion logic
    # For example, using SQLAlchemy or any other database library
    return

def get_last_updated(engine, table_name):
    with engine.connect() as conn:
        sql = text("SELECT last_updated FROM data_status WHERE table_name = :name")
        row = conn.execute(sql, {"name":table_name}).fetchone()
        if row[0] is None:
            return None
        last_updated = row[0]
        return last_updated if isinstance(last_updated, datetime) else datetime.fromisoformat(last_updated)


def update_last_updated(engine, table_name):
    print("Updating last_updated")
    now_utc = datetime.now(timezone.utc)
    sql = text("""INSERT INTO data_status (table_name, last_updated) 
                  VALUES (:name, :updated) ON CONFLICT (table_name) 
                  DO UPDATE SET last_updated = :updated""")
    with engine.begin() as conn:
         conn.execute(sql, {"name": table_name, "updated": now_utc})
    return

def should_fetch_data(engine, table_name, max_days):
    last = get_last_updated(engine, table_name)
    if last is None or pd.isna(last):
        return True
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - last > timedelta(days=max_days)



