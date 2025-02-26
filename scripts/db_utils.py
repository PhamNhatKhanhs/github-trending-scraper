# scripts/db_utils.py
import sqlite3
import os
from datetime import datetime
import pandas as pd

DB_PATH = os.path.join("db", "github_trending.db")

def init_db():
    """
    Tạo file DB và bảng (nếu chưa tồn tại).
    Dùng bảng 'github_trending' để lưu nhiều lần scrape.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS github_trending (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scrape_date TEXT,
        full_name TEXT,
        description TEXT,
        language TEXT,
        stars INTEGER,
        link TEXT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

def append_data_to_db(df):
    """
    Ghi DataFrame vào bảng 'github_trending' theo kiểu append (không xóa dữ liệu cũ).
    Thêm cột 'scrape_date' (ngày giờ) từ DF nếu cần.
    """
    # Kết nối
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("github_trending", conn, if_exists="append", index=False)
    conn.close()

def get_data_from_db(limit=10):
    """
    Lấy dữ liệu mới nhất (hoặc tất cả), trả về DataFrame.
    """
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM github_trending ORDER BY id DESC LIMIT {limit}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
