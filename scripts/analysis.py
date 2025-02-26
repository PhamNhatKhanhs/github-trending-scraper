# scripts/analysis.py
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
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

    if df.empty:
        print("No data found in the database. Please run the scraper first.")
        return

    # Chuyển scrape_date sang datetime
    df["scrape_date"] = pd.to_datetime(df["scrape_date"])
    
    # 1. Language Distribution Analysis
    plt.figure(figsize=(12, 6))
    lang_counts = df['language'].value_counts().head(10)
    if not lang_counts.empty:
        sns.barplot(x=lang_counts.values, y=lang_counts.index)
        plt.title('Top 10 Programming Languages in Trending Repositories')
        plt.xlabel('Number of Repositories')
        plt.savefig('data/language_distribution.png')
    plt.close()

    # 2. Star Change Analysis
    plt.figure(figsize=(12, 6))
    star_changes = df.groupby('language')['star_change'].mean().sort_values(ascending=False).head(10)
    if not star_changes.empty:
        sns.barplot(x=star_changes.values, y=star_changes.index)
        plt.title('Average Star Changes by Language')
        plt.xlabel('Average Star Change')
        plt.savefig('data/star_changes.png')
    plt.close()

    # 3. Topic Analysis
    all_topics = []
    for topics_str in df['topics'].dropna():
        if topics_str:
            all_topics.extend(topics_str.split(','))
    topic_counts = pd.Series(all_topics).value_counts().head(15)
    
    if not topic_counts.empty:
        plt.figure(figsize=(12, 6))
        sns.barplot(x=topic_counts.values, y=topic_counts.index)
        plt.title('Most Common Repository Topics')
        plt.xlabel('Number of Occurrences')
        plt.savefig('data/topic_distribution.png')
    plt.close()

    # 4. Contributor Count Analysis
    plt.figure(figsize=(12, 6))
    contrib_by_lang = df.groupby('language')['contributor_count'].mean().sort_values(ascending=False).head(10)
    if not contrib_by_lang.empty:
        sns.barplot(x=contrib_by_lang.values, y=contrib_by_lang.index)
        plt.title('Average Number of Contributors by Language')
        plt.xlabel('Average Number of Contributors')
        plt.savefig('data/contributor_analysis.png')
    plt.close()

    # Generate summary report
    with open('data/analysis_report.md', 'w', encoding='utf-8') as f:
        f.write('# GitHub Trending Analysis Report\n\n')
        f.write(f'Report generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        
        f.write('## Key Findings\n\n')
        if not lang_counts.empty:
            f.write(f'1. Most Popular Language: {lang_counts.index[0]} with {lang_counts.values[0]} repositories\n')
        if not star_changes.empty:
            f.write(f'2. Highest Average Star Change: {star_changes.index[0]} with {star_changes.values[0]:.0f} stars\n')
        if not topic_counts.empty:
            f.write(f'3. Most Common Topic: {topic_counts.index[0]} (used {topic_counts.values[0]} times)\n')
        if not contrib_by_lang.empty:
            f.write(f'4. Language with Most Contributors: {contrib_by_lang.index[0]} (avg: {contrib_by_lang.values[0]:.0f})\n')
def main():
    print("=== Starting GitHub Trending Analysis ===")
    analyze_by_date()
    print("=== Analysis Complete ===")
    print("Check the 'data' directory for visualization results and the analysis report.")

if __name__ == "__main__":
    main()
