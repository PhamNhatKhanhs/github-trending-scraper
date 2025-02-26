import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

DB_PATH = 'db/github_trending.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            description TEXT,
            language TEXT,
            stars INTEGER,
            star_change INTEGER,
            contributor_count INTEGER,
            link TEXT,
            scrape_date DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

def append_data_to_db(df):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('repositories', conn, if_exists='append', index=False)
    conn.close()

def get_data_from_db(days=7):
    conn = sqlite3.connect(DB_PATH)
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    query = f"SELECT * FROM repositories WHERE scrape_date >= '{cutoff_date}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_latest_data():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM repositories WHERE scrape_date = (SELECT MAX(scrape_date) FROM repositories)"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df
