# Mô-đun chứa các tiện ích thao tác với cơ sở dữ liệu SQLite
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# Đường dẫn đến file cơ sở dữ liệu
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'github_trending.db')

def init_db():
    # Khởi tạo cơ sở dữ liệu và tạo bảng nếu chưa tồn tại
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tạo bảng repositories nếu chưa tồn tại
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
    # Thêm dữ liệu mới vào cơ sở dữ liệu
    # Tham số:
    #   df: DataFrame chứa thông tin các repository cần lưu
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('repositories', conn, if_exists='append', index=False)
    conn.close()

def get_data_from_db(days=7):
    # Lấy dữ liệu từ cơ sở dữ liệu trong khoảng thời gian chỉ định
    # Tham số:
    #   days: Số ngày cần lấy dữ liệu (mặc định: 7 ngày)
    # Trả về:
    #   DataFrame chứa thông tin các repository
    conn = sqlite3.connect(DB_PATH)
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    query = f"SELECT * FROM repositories WHERE scrape_date >= '{cutoff_date}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_latest_data():
    # Lấy dữ liệu mới nhất từ cơ sở dữ liệu
    # Trả về:
    #   DataFrame chứa thông tin các repository của lần cập nhật gần nhất
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM repositories WHERE scrape_date = (SELECT MAX(scrape_date) FROM repositories)"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df
