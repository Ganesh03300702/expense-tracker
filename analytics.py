import pandas as pd
import sqlite3
from database import DB_NAME

def get_expenses_df():
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM expenses", conn)
        conn.close()
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def get_category_summary():
    df = get_expenses_df()
    if df.empty:
        return {}
    summary = df.groupby('category')['amount'].sum().to_dict()
    return summary

def get_monthly_summary():
    df = get_expenses_df()
    if df.empty:
        return {}
    # Group by Year-Month string for sorting/display
    df['month'] = df['date'].dt.strftime('%Y-%m')
    summary = df.groupby('month')['amount'].sum().to_dict()
    return summary

def get_total_spending():
    df = get_expenses_df()
    if df.empty:
        return 0.0
    return df['amount'].sum()
