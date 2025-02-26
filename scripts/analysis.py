# scripts/analysis.py
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from db_utils import get_data_from_db

def analyze_top_languages():
    # Lấy 200 dòng mới nhất (demo)
    df = get_data_from_db(limit=200)
    # Đếm frequency ngôn ngữ
    lang_count = df["language"].value_counts().head(10)
    print("Top 10 languages among the latest 200 repos:")
    print(lang_count)

    lang_count.plot(kind="bar")
    plt.title("Top 10 languages in the latest 200 trending repos")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def analyze_by_date():
    # Lấy *tất cả* data
    conn = sqlite3.connect("db/github_trending.db")
    df = pd.read_sql("SELECT * FROM github_trending", conn)
    conn.close()

    # Chuyển scrape_date sang datetime
    df["scrape_date"] = pd.to_datetime(df["scrape_date"])

    # Tùy ý: ví dụ xem số repo theo language và scrape_date
    # Chỉ minh họa:
    daily_lang_count = df.groupby([df["scrape_date"].dt.date, "language"])["full_name"].count().unstack().fillna(0)
    print(daily_lang_count.head())

    # Bạn có thể vẽ heatmap, line chart, v.v.

if __name__ == "__main__":
    analyze_top_languages()
    analyze_by_date()
